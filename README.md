## Deployment

### Packaging and Deployment Using Terraform

The Lambda function is packaged and deployed using Terraform to ensure a fully automated and repeatable deployment process.

Terraform uses the `archive_file` data source to package the Lambda source code (`snapshot_cleaner.py`) into a ZIP file during the `terraform apply` phase. This ZIP file is then uploaded directly to AWS Lambda using the `aws_lambda_function` resource.

#### Deployment Steps

1. Navigate to the Terraform directory:
   cd terraform
2. Initialize Terraform providers and modules:
   terraform init
3. Deploy the infrastructure and Lambda function:
   terraform apply

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   
# EC2 Snapshot Cleaner (Lambda in VPC)

This project provisions AWS infrastructure and deploys a Lambda function that deletes EBS snapshots older than one year (default: 365 days). The Lambda runs inside a private subnet in a VPC and is triggered daily via EventBridge.

## Why Terraform?
Terraform is cloud-agnostic, widely adopted, and offers excellent dependency management and packaging workflows (e.g., archive_file for Lambda zip).

## What gets created?
- VPC with:
  - 1 public subnet (hosts NAT Gateway)
  - 1 private subnet (Lambda runs here)
  - Internet Gateway, NAT Gateway, route tables
- Security Group for Lambda
- IAM role + policy allowing:
  - ec2:DescribeSnapshots
  - ec2:DeleteSnapshot
  - CloudWatch Logs permissions
- Lambda function deployed from local `lambda/` folder
- EventBridge Rule (daily schedule) + permissions to invoke Lambda

## How to deploy (IaC)
From the `terraform/` directory:
terraform init
terraform apply

## How Lambda code is deployed

Terraform zips the lambda/ folder and uploads it using:
archive_file -> local zip
aws_lambda_function -> deploys zip to Lambda

## VPC configuration (Lambda in private subnet)

Lambda is configured with:
Subnet IDs: the private subnet ID from Terraform output
Security group IDs: Lambda SG from Terraform output

## Why a NAT Gateway?

The Lambda is in a private subnet and still needs to call AWS public APIs (EC2 API) and send logs to CloudWatch Logs.

NAT provides outbound access without making the subnet public.
(Alternative: use VPC interface endpoints for EC2 + Logs where applicable, but NAT is simpler and broadly supported.)

## Configuration
Environment variables:
RETENTION_DAYS (default 365)
DRY_RUN (default false). If true, logs what would be deleted but does not delete.
Terraform variables:
aws_region (default us-east-1)
schedule_expression (default cron(0 3 * * ? *))

## Assumptions
Only snapshots owned by this AWS account are considered (OwnerIds=["self"]).
Region is set via Terraform provider aws_region.
Snapshots older than RETENTION_DAYS are candidates for deletion.

## Monitoring
CloudWatch Logs: /aws/lambda/<function-name>
EventBridge Rule metrics and Lambda invocation/error metrics in CloudWatch Metrics
Recommended alarms:
Lambda Errors > 0
Lambda Throttles > 0
Invocations == 0 (to detect schedule issues)

