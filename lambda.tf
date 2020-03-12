module "lambda" {
  source = "github.com/claranet/terraform-aws-lambda?ref=v1.1.0"

  function_name = var.name
  description   = "Manages ASG instance alarms"
  handler       = "lambda.lambda_handler"
  runtime       = "python3.6"
  layers        = var.lambda_layers
  timeout       = 30

  source_path = "${path.module}/lambda.py"

  environment = {
    variables = {
      ALARM_TEMPLATES_BUCKET = aws_s3_bucket.alarm_templates.id
    }
  }

  policy = {
    json = data.aws_iam_policy_document.lambda.json
  }

  tags = var.lambda_tags
}

data "aws_iam_policy_document" "lambda" {
  statement {
    effect = "Allow"

    actions = [
      "autoscaling:DescribeAutoScalingGroups",
    ]

    resources = [
      "*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "cloudwatch:DeleteAlarms",
      "cloudwatch:DescribeAlarms",
      "cloudwatch:PutMetricAlarm",
    ]

    resources = [
      "*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "arn:aws:s3:::${aws_s3_bucket.alarm_templates.id}/*",
    ]
  }
}
