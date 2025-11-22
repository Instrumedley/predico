# ACM Certificate (for HTTPS)
resource "aws_acm_certificate" "main" {
  count            = var.domain_name != "" ? 1 : 0
  domain_name      = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = [
    "*.${var.domain_name}"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.project_name}-cert"
  }
}

# Certificate Validation
resource "aws_acm_certificate_validation" "main" {
  count           = var.domain_name != "" ? 1 : 0
  certificate_arn = aws_acm_certificate.main[0].arn
  # Note: You'll need to add DNS validation records manually or use Route53
}

