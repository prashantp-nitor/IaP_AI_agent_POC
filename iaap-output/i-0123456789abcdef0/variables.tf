variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_name" {
  description = "Name tag for the EC2 instance"
  type        = string
  default     = "i-0123456789abcdef0"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "iam_instance_profile" {
  description = "IAM Instance Profile"
  type        = string
  default     = ""
}

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}
