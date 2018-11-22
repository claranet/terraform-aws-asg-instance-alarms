data "external" "template" {
  program = ["python", "${path.module}/template.py"]

  query = {
    ActionsEnabled                   = "${var.ActionsEnabled}"
    AlarmActions                     = "${jsonencode(var.AlarmActions)}"
    AlarmDescription                 = "${var.AlarmDescription}"
    ComparisonOperator               = "${var.ComparisonOperator}"
    Dimensions                       = "${jsonencode(var.Dimensions)}"
    EvaluateLowSampleCountPercentile = "${var.EvaluateLowSampleCountPercentile}"
    EvaluationPeriods                = "${var.EvaluationPeriods}"
    ExtendedStatistic                = "${var.ExtendedStatistic}"
    InsufficientDataActions          = "${jsonencode(var.InsufficientDataActions)}"
    MetricName                       = "${var.MetricName}"
    Namespace                        = "${var.Namespace}"
    OKActions                        = "${jsonencode(var.OKActions)}"
    Period                           = "${var.Period}"
    Statistic                        = "${var.Statistic}"
    Threshold                        = "${var.Threshold}"
    TreatMissingData                 = "${var.TreatMissingData}"
    Unit                             = "${var.Unit}"
  }
}

resource "aws_s3_bucket_object" "template" {
  bucket  = "${var.bucket}"
  key     = "${lookup(data.external.template.result, "key")}"
  content = "${lookup(data.external.template.result, "content")}"
  etag    = "${lookup(data.external.template.result, "etag")}"
}
