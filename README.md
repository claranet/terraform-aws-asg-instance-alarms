# tf-aws-asg-instance-alarms

This module manages EC2 instance alarms for an auto scaling group. It will automatically create and delete alarms for EC2 instances using EC2 instance metrics.

With the right metrics being pushed into CloudWatch, plus this module, you can have alerts for EC2 instances without the need for any monitoring servers.

## Components

### Lambda function

Use the `tf-aws-asg-instance-alarms` module once per AWS account to create the Lambda function and associated resources required to manage the instance alarms.

The Lambda function is triggered whenever an instance is launched or terminated. It creates and deletes alarms specific to that instance.

The Lambda function also runs on a schedule to ensure that all alarms within the AWS account are configured correctly. For example, if the Terraform code is changed to add a new alarm to an ASG, the scheduled function will create the alarm for all running instances that should have it.

### Alarm templates

Use the `tf-aws-asg-instance-alarms/template` submodule to create alarm templates. Each template is used to create one specific alarm, but variables in the template allow for it to be reused across multiple ASGs and instances.

Alarm template usage maps directly to the CloudWatch PutMetricAlarm API, except that it has variables using the `{{name}}` syntax. The supported template variables are:

* `{{asg.AutoScalingGroupName}}`
* `{{asg.Tags.AnyTagNameHere}}`
* `{{instance.InstanceId}}`

### ASG tags

The `tf-aws-asg-instance-alarms/template` submodule has a `tags` output that can be added to ASGs to enable that alarm. The Lambda function uses these ASG tags to determine which alarms to create for the EC2 instances.

## Example

```javascript
// Create the Lambda function and asssociated resources once per AWS account.

module "instance_alarms" {
  source = "tf-aws-asg-instance-alarms"
  name   = "${var.customer}-asg-instance-alarms"
}

// Create any number of alarm templates.

module "cpu_credits_alarm" {
  source = "tf-aws-asg-instance-alarms/template"
  bucket = "${module.instance_alarms.bucket}"

  AlarmDescription = "{{instance.InstanceId}} is low on CPU credits"
  Namespace        = "AWS/EC2"
  MetricName       = "CPUCreditBalance"

  Dimensions = [
    {
      Name  = "InstanceId"
      Value = "{{instance.InstanceId}}"
    },
  ]

  Statistic          = "Average"
  ComparisonOperator = "LessThanOrEqualToThreshold"
  Threshold          = 20
  Period             = 60
  EvaluationPeriods  = 5

  OKActions = [
    "${aws_sns_topic.slack.arn}",
  ]

  AlarmActions = [
    "${aws_sns_topic.slack.arn}",
  ]

  InsufficientDataActions = [
    "${aws_sns_topic.slack.arn}",
  ]
}

module "memory_alarm" {
  source = "tf-aws-asg-instance-alarms/template"
  bucket = "${module.instance_alarms.bucket}"

  AlarmDescription = "{{instance.InstanceId}} is low on memory"
  Namespace        = "Telegraf/EC2"
  MetricName       = "mem_used_percent"

  Dimensions = [
    {
      Name  = "asg-name"
      Value = "{{asg.AutoScalingGroupName}}"
    },
    {
      Name  = "environment"
      Value = "{{asg.Tags.Environment}}"
    },
    {
      Name  = "instance-id"
      Value = "{{instance.InstanceId}}"
    },
  ]

  Statistic          = "Maximum"
  ComparisonOperator = "GreaterThanOrEqualToThreshold"
  Threshold          = 80
  Period             = 60
  EvaluationPeriods  = 5

  OKActions = [
    "${aws_sns_topic.slack.arn}",
  ]

  AlarmActions = [
    "${aws_sns_topic.slack.arn}",
  ]

  InsufficientDataActions = [
    "${aws_sns_topic.slack.arn}",
  ]
}

// Attach the alarm templates to ASGs.

module "bastion_asg" {
  extra_tags = [
    {
      key = "${module.cpu_credits_alarm.tag}"
      value = ""
    },
    {
      key = "${module.memory_alarm.tag}"
      value = ""
    },
  ]
}
```
