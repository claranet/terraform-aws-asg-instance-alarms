provider "aws" {
  region = "eu-west-2"
}

resource "random_pet" "test" {
  prefix = "tf-alarms-test"
}

resource "aws_sns_topic" "test" {
  name = random_pet.test.id
}

module "instance_alarms" {
  source = "../"

  name = random_pet.test.id
}

module "cpu_credits_alarm" {
  source = "../modules/template"

  bucket = module.instance_alarms.bucket

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
    aws_sns_topic.test.arn,
  ]

  AlarmActions = [
    aws_sns_topic.test.arn,
  ]

  InsufficientDataActions = [
    aws_sns_topic.test.arn,
  ]
}
