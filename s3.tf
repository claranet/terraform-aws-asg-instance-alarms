# Create an S3 bucket for storing alarm templates.

resource "random_id" "bucket_name" {
  byte_length = 8
  prefix      = "${var.name}-"
}

resource "aws_s3_bucket" "alarm_templates" {
  bucket = random_id.bucket_name.hex
  acl    = "private"
  tags   = var.s3_tags
}
