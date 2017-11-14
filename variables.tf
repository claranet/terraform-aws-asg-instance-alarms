variable "name" {
  default = "tf-aws-asg-instance-alarms"
}

variable "schedule" {
  default = "rate(5 minutes)"
}
