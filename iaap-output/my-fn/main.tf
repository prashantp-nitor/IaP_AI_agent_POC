terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_lambda_function" "fn" {
  function_name = var.function_name
  role          = var.lambda_role_arn
  runtime       = "python3.12"
  handler       = "lambda_function.lambda_handler"
  filename      = var.filename
  memory_size   = var.memory_size
  timeout       = var.timeout
}
