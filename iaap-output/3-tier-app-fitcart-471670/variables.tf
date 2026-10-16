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

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {
    ManagedBy = "IAAP"
    environment = "prod"
    owner = "user@company.com"
    project = "3-tier-app-fitcart"
    job_id = "471670d7-f56f-42a4-b9c6-9a1a98617582"
    project_folder = "3-tier-app-fitcart-471670"
  }
}

variable "vnet_name" {
  description = "Name of the Azure Virtual Network"
  type        = string
  default     = "3-tier-app-fitcart-network"
}

variable "address_space" {
  description = "Address space for Virtual Network"
  type        = list(string)
  default     = [
    "10.0.0.0/16",
  ]
}

variable "postgres_server_name" {
  description = "PostgreSQL flexible server name"
  type        = string
  default     = "3-tier-app-fit-dbnew161026"
}

variable "postgres_sku_name" {
  description = "PostgreSQL compute SKU"
  type        = string
  default     = "B_Standard_B2s"
}

variable "postgres_version" {
  description = "PostgreSQL major version"
  type        = string
  default     = "15"
}

variable "postgres_storage_mb" {
  description = "Storage size in MB"
  type        = number
  default     = 32768
}

variable "postgres_backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 14
}

variable "postgres_admin_username" {
  description = "PostgreSQL administrator login"
  type        = string
  default     = "pgadmin"
}

variable "postgres_admin_password" {
  description = "PostgreSQL administrator password (override via TF_VAR_postgres_admin_password)"
  type        = string
  default     = "_*nPNZv%F0nMXfCA"
  sensitive   = true
}

variable "postgres_database_name" {
  description = "Default database name"
  type        = string
  default     = "appdb"
}
