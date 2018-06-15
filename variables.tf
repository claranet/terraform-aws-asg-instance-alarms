variable "name" {
  default = "terraform-aws-asg-instance-alarms"
}

variable "schedule" {
  default = "rate(5 minutes)"
}
