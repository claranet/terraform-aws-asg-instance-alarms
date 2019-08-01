# Trigger the Lambda function with these instance events.

resource "aws_cloudwatch_event_rule" "events" {
  name = var.name

  event_pattern = <<PATTERN
{
  "source": [
    "aws.autoscaling",
    "aws.ec2"
  ],
  "detail-type": [
      "EC2 Instance Launch Successful",
      "EC2 Instance State-change Notification"
  ]
}
PATTERN
}

resource "aws_cloudwatch_event_target" "events" {
  target_id = "${var.name}-events"
  rule      = aws_cloudwatch_event_rule.events.name
  arn       = module.lambda.function_arn
}

resource "aws_lambda_permission" "events" {
  statement_id  = "${var.name}-events"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.events.arn
}

# Also check for changes regularly.

resource "aws_cloudwatch_event_rule" "schedule" {
  count               = var.schedule == "" ? 0 : 1
  name                = "${var.name}-schedule"
  schedule_expression = var.schedule
}

resource "aws_cloudwatch_event_target" "schedule" {
  count     = var.schedule == "" ? 0 : 1
  target_id = "${var.name}-schedule"
  rule      = aws_cloudwatch_event_rule.schedule.name
  arn       = module.lambda.function_arn
}

resource "aws_lambda_permission" "schedule" {
  count         = var.schedule == "" ? 0 : 1
  statement_id  = "${var.name}-schedule"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule.arn
}
