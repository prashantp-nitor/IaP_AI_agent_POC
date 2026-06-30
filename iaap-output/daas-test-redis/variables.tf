variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "cluster_id" {
  description = "ElastiCache cluster identifier"
  type        = string
  default     = "daas-test-redis"
}

variable "node_type" {
  description = "Cache node type"
  type        = string
  default     = "cache.t4g.micro"
}

variable "engine_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.1"
}

variable "parameter_group_family" {
  description = "Cache parameter group family"
  type        = string
  default     = "redis7"
}

variable "port" {
  description = "Port the cache listens on"
  type        = number
  default     = 6379
}

variable "vpc_id" {
  description = "VPC ID for the cache security group"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for the cache subnet group"
  type        = list(string)
  default     = []
}

variable "security_group_ids" {
  description = "Security group IDs to attach to the cache"
  type        = list(string)
  default     = []
}

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}
