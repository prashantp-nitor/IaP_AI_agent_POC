variable "region" {
  description = "AWS region"
  type        = string
  default     = "East US"
}

variable "vpc_name" {
  description = "Name prefix for the VPC and all sub-resources"
  type        = string
  default     = "test-vpc-aws"
}

variable "cidr_block" {
  description = "IPv4 CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}
