variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "db_identifier" {
  description = "RDS instance identifier"
  type        = string
  default     = "fitcart-test-rds"
}

variable "engine" {
  description = "Database engine"
  type        = string
  default     = "mysql"
}

variable "engine_version" {
  description = "Database engine version"
  type        = string
  default     = "8.0"
}

variable "db_family" {
  description = "DB parameter group family"
  type        = string
  default     = "mysql8.0"
}

variable "major_engine_version" {
  description = "Major engine version"
  type        = string
  default     = "8.0"
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_username" {
  description = "Master username"
  type        = string
  default     = "test-demo"
}

variable "db_password" {
  description = "Master password (supplied via CI secret)"
  type        = string
  sensitive   = true
}

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}
