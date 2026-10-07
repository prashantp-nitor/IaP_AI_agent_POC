variable "region" {
  description = "Azure region for all resources"
  type        = string
  default     = "eastus"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "AZET-RG-Daas-Platform"
}

variable "server_name" {
  description = "Globally unique PostgreSQL flexible server name"
  type        = string
  default     = "postgres-test"
}

variable "sku_name" {
  description = "Compute SKU (e.g. B_Standard_B1ms, GP_Standard_D2s_v3)"
  type        = string
  default     = "B_Standard_B2s"
}

variable "pg_version" {
  description = "PostgreSQL major version (e.g. 13, 14, 15, 16)"
  type        = string
  default     = "14"
}

variable "storage_mb" {
  description = "Storage size in MB"
  type        = number
  default     = 32768
}

variable "backup_retention_days" {
  description = "Backup retention period in days (7-35)"
  type        = number
  default     = 7
}

variable "administrator_login" {
  description = "PostgreSQL administrator login"
  type        = string
  default     = "pgadmin"
}

variable "administrator_password" {
  description = "PostgreSQL administrator password (override via TF_VAR or secret)"
  type        = string
  default     = "Admin@123"
  sensitive   = true
}

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}
