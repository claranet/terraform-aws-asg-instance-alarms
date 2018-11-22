output "tag" {
  value = "InstanceAlarm:${aws_s3_bucket_object.template.key}"
}
