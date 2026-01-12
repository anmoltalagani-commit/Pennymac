output "vpc_id" {
  value = aws_vpc.this.id
}

output "private_subnet_id" {
  value = aws_subnet.private.id
}

output "lambda_security_group_id" {
  value = aws_security_group.lambda_sg.id
}

output "lambda_function_name" {
  value = aws_lambda_function.snapshot_cleaner.function_name
}
