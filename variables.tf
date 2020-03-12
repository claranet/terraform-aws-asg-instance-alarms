variable "name" {
  default = "terraform-aws-asg-instance-alarms"
}

variable "schedule" {
  default = "rate(5 minutes)"
}

variable "lambda_layers" {
  default = []
}

variable "s3_tags" {
  type    = map
  default = {}
}

variable "lambda_tags" {
  type    = map
  default = {}
}
