output "bucket" {
  value = "${aws_s3_bucket.alarm_templates.id}"
}
