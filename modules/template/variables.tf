variable "bucket" {
  description = "The S3 bucket used to store the template file."
  type        = string
}

variable "ActionsEnabled" {
  default = true
}

variable "AlarmActions" {
  default = []
}

variable "AlarmDescription" {
  default = ""
}

variable "ComparisonOperator" {
  type = string
}

variable "Dimensions" {
  default = []
}

variable "EvaluateLowSampleCountPercentile" {
  default = ""
}

variable "EvaluationPeriods" {
  type = string
}

variable "ExtendedStatistic" {
  default = ""
}

variable "InsufficientDataActions" {
  default = []
}

variable "MetricName" {
  type = string
}

variable "Namespace" {
  type = string
}

variable "OKActions" {
  default = []
}

variable "Period" {
  type = string
}

variable "Statistic" {
  default = ""
}

variable "Threshold" {
  type = string
}

variable "TreatMissingData" {
  default = "missing"
}

variable "Unit" {
  default = ""
}
