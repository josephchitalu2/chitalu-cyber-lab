resource "aws_security_group" "prod_db_sg" {
  name        = "prod-postgres-sg"
  description = "Allow database and SSH access"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "customer_exports" {
  bucket = "chitalu-prod-customer-exports"
  acl    = "public-read"
}
