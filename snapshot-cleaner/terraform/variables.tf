variable "name" {
  type    = string
  default = "snapshot-cleaner"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "public_subnet_cidr" {
  type    = string
  default = "10.20.1.0/24"
}

variable "private_subnet_cidr" {
  type    = string
  default = "10.20.2.0/24"
}

variable "retention_days" {
  type    = number
  default = 365
}

variable "dry_run" {
  type    = bool
  default = false
}

# Daily at 03:00 UTC by default
variable "schedule_expression" {
  type    = string
  default = "cron(0 3 * * ? *)"
}
