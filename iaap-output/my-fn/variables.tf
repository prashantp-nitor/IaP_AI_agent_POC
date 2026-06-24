variable "function_name" {
  type = string
  default = "my-fn"
}

variable "aws_region" {
  type = string
  default = "us-west-2"
}

variable "memory_size" {
  type = number
  default = 512
}

variable "timeout" {
  type = number
  default = 10
}

variable "lambda_role_arn" {
  type = string
  default = "arn:aws:iam::123456789012:role/lambda-exec-role"
}

variable "filename" {
  type = string
  default = "lambda.zip"
}
