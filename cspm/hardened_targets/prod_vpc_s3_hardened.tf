resource "aws_security_group" "prod_db_sg" {
  name        = "prod-postgres-sg-hardened"
  description = "Restrict PostgreSQL access to private VPC CIDR only"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.10.0/24"]
  }
}

resource "aws_s3_bucket" "customer_exports" {
  bucket = "chitalu-prod-customer-exports-secure"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "customer_exports_sse" {
  bucket = aws_s3_bucket.customer_exports.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
