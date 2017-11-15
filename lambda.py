import boto3
import decimal
import json
import os


ALARM_NAME_PREFIX = 'InstanceAlarm:'
ALARM_TEMPLATES_BUCKET = os.environ['ALARM_TEMPLATES_BUCKET']
ALARM_TEMPLATES_CACHE = {}

# Maximum number of alarms to delete per API call.
DELETE_ALARMS_MAX_NAMES = 100


autoscaling = boto3.client('autoscaling')
cloudwatch = boto3.client('cloudwatch')
s3 = boto3.client('s3')


def create_instance_alarms(asg_name, instance_id):
    """
    Creates alarms for the specified EC2 instance.

    """

    asgs = describe_auto_scaling_groups(
        AutoScalingGroupNames=[asg_name],
    )
    for asg in asgs:
        alarms_to_create = get_alarms_to_create(asg, instance_id)
        for alarm in alarms_to_create:
            print('Creating alarm: {}'.format(alarm['AlarmName']))
            put_metric_alarm(**alarm)


def delete_alarms(alarm_names):
    """
    Deletes the specified alarms.

    """

    # Delete as many alarms as possible in one API call.
    # Use a list and go through it in chunks.
    alarm_names = list(alarm_names)
    while alarm_names:

        # Delete a chunk of alarms.
        response = cloudwatch.delete_alarms(
            AlarmNames=alarm_names[:DELETE_ALARMS_MAX_NAMES],
        )
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception('ERROR: {}'.format(response))

        # Move to the next chunk.
        alarm_names = alarm_names[DELETE_ALARMS_MAX_NAMES:]


def delete_instance_alarms(instance_id):
    """
    Delete all alarms that exist for the specified EC2 instance.

    """

    # This Lambda function always create alarms for instances using a standard
    # prefix and then the instance id. Find any delete any alarms that have
    # this naming convention and this instance id.

    alarms = describe_alarms(
        AlarmNamePrefix=ALARM_NAME_PREFIX + instance_id,
    )
    alarm_names = [alarm['AlarmName'] for alarm in alarms]

    print('Deleting alarms: {}'.format(alarm_names))
    delete_alarms(alarm_names)


def describe_alarms(**kwargs):
    """
    Returns CloudWatch Metric Alarms.

    """

    paginator = cloudwatch.get_paginator('describe_alarms')
    pages = paginator.paginate(**kwargs)
    for page in pages:
        if page['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception('ERROR: {}'.format(page))
        for alarm in page['MetricAlarms']:
            yield alarm


def describe_auto_scaling_groups(**kwargs):
    """
    Returns Auto Scaling Groups.

    """

    paginator = autoscaling.get_paginator('describe_auto_scaling_groups')
    pages = paginator.paginate(**kwargs)
    for page in pages:
        if page['ResponseMetadata']['HTTPStatusCode'] != 200:
            raise Exception('ERROR: {}'.format(page))
        for asg in page['AutoScalingGroups']:
            yield asg


def full_sweep():
    """
    Creates any instance alarms that should exist but don't, and deletes
    any instance alarms that shouldn't exist but do.

    """

    # Get a list of all instance alarms in the AWS account.
    found_alarm_names = set()
    alarms = describe_alarms(
        AlarmNamePrefix=ALARM_NAME_PREFIX,
    )
    for alarm in alarms:
        alarm_name = alarm['AlarmName']
        found_alarm_names.add(alarm_name)

    # Go through all ASGs and their EC2 instances and create an alarms that
    # should exist but don't. Build a list of the alarms that should exist.
    expected_alarm_names = set()
    for asg in describe_auto_scaling_groups():
        for instance in asg['Instances']:
            if instance['LifecycleState'] != 'InService':
                continue
            alarms = get_alarms_to_create(asg, instance['InstanceId'])
            for alarm in alarms:
                alarm_name = alarm['AlarmName']
                expected_alarm_names.add(alarm_name)
                if alarm_name not in found_alarm_names:
                    print('Creating missing alarm: {}'.format(alarm_name))
                    put_metric_alarm(**alarm)

    # Delete any instance alarms that shouldn't exist.
    orphan_alarm_names = found_alarm_names - expected_alarm_names
    if orphan_alarm_names:
        print('Deleting orphan alarms: {}'.format(orphan_alarm_names))
        delete_alarms(orphan_alarm_names)


def get_alarm_keys(asg):
    """
    Returns alarm keys as defined by the ASG's tags.

    """

    for tag in asg['Tags']:
        tag_key = tag['Key']
        if tag_key.startswith(ALARM_NAME_PREFIX):
            alarm_key = tag_key[len(ALARM_NAME_PREFIX):]
            yield alarm_key


def get_alarms_to_create(asg, instance_id):
    """
    Returns alarm dictionaries that should be created for an EC2 instance.

    """

    for alarm_key in get_alarm_keys(asg):

        # Read alarm templates from S3 and cache them in memory.
        if alarm_key not in ALARM_TEMPLATES_CACHE:
            ALARM_TEMPLATES_CACHE[alarm_key] = get_s3_object_body(
                Bucket=ALARM_TEMPLATES_BUCKET,
                Key=alarm_key,
            )
        template_string = ALARM_TEMPLATES_CACHE[alarm_key]

        # Render the template using variables from the ASG and instance.
        template_variables = {
            'asg.AutoScalingGroupName': asg['AutoScalingGroupName'],
            'instance.InstanceId': instance_id,
        }
        for tag in asg['Tags']:
            var_name = 'asg.Tags.' + tag['Key']
            template_variables[var_name] = tag['Value']
        for var_name, value in template_variables.items():
            template_string = template_string.replace(
                '{{' + var_name + '}}',
                value,
            )

        # It should be valid JSON now.
        alarm = json.loads(template_string)

        # Set the alarm name programatically so it can be found and deleted
        # after the instance has been terminated.
        alarm['AlarmName'] = ALARM_NAME_PREFIX + instance_id + ':' + alarm_key

        yield alarm


def get_s3_object_body(**kwargs):
    """
    Returns the content of an object in S3.

    """

    response = s3.get_object(**kwargs)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception('ERROR: {}'.format(response))

    return response['Body'].read().decode('utf-8')


def put_metric_alarm(**alarm):
    """
    Creates a CloudWatch Metric Alarm.

    """

    # Convert numeric fields into appropriate types.
    alarm['EvaluationPeriods'] = int(alarm['EvaluationPeriods'])
    alarm['Period'] = int(alarm['Period'])
    alarm['Threshold'] = decimal.Decimal(alarm['Threshold'])

    # Create the alarm.
    response = cloudwatch.put_metric_alarm(**alarm)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception('ERROR: {}'.format(response))


def lambda_handler(event, context):
    print('Received event: {}'.format(event))
    if event['detail-type'] == 'EC2 Instance Launch Successful':
        asg_name = event['detail']['AutoScalingGroupName']
        instance_id = event['detail']['EC2InstanceId']
        create_instance_alarms(asg_name, instance_id)
    elif event['detail-type'] == 'EC2 Instance Terminate Successful':
        instance_id = event['detail']['EC2InstanceId']
        delete_instance_alarms(instance_id)
    else:
        full_sweep()
