variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "cluster_id" {
  description = "ElastiCache replication group ID"
  type        = string
  default     = "daas-test-redis"
}

variable "vpc_id" {
  description = "VPC ID for the security group"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for the ElastiCache subnet group (comma-separated in the form)"
  type        = list(string)
  default     = []
}

variable "node_type" {
  description = "ElastiCache node type (e.g. cache.t3.micro)"
  type        = string
  default     = "cache.t3.micro"
}

variable "num_cache_nodes" {
  description = "Number of cache nodes (1 = single-node; 2+ enables replicas)"
  type        = number
  default     = 1
}

variable "automatic_failover_enabled" {
  description = "Enable automatic failover (requires num_cache_nodes >= 2)"
  type        = bool
  default     = false
}

variable "multi_az_enabled" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}
