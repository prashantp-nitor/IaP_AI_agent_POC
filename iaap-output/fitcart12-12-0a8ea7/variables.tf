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
    project = "fitcart12-12"
    job_id = "0a8ea725-b547-4f16-8785-ff8c68e9a021"
    project_folder = "fitcart12-12-0a8ea7"
  }
}

variable "cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
  default     = "fitcart12-12-aks"
}

variable "kubernetes_version" {
  description = "Kubernetes version for AKS"
  type        = string
  default     = "1.34.4"
}

variable "node_count" {
  description = "Number of nodes in the default node pool"
  type        = number
  default     = 2
}

variable "node_vm_size" {
  description = "VM size for default node pool nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "network_plugin" {
  description = "Network plugin (azure or kubenet)"
  type        = string
  default     = "azure"
}

variable "network_policy" {
  description = "Network policy engine"
  type        = string
  default     = "azure"
}

variable "dns_prefix" {
  description = "DNS prefix for AKS cluster"
  type        = string
  default     = "fitcart12-12-aks"
}

variable "enable_rbac" {
  description = "Enable Kubernetes RBAC"
  type        = bool
  default     = true
}

variable "os_disk_size_gb" {
  description = "OS disk size in GB"
  type        = number
  default     = 30
}

variable "postgres_server_name" {
  description = "PostgreSQL flexible server name"
  type        = string
  default     = "fitcart12-12-db"
}

variable "postgres_sku_name" {
  description = "PostgreSQL compute SKU"
  type        = string
  default     = "GP_Standard_D2s_v3"
}

variable "postgres_version" {
  description = "PostgreSQL major version"
  type        = string
  default     = "14"
}

variable "postgres_storage_mb" {
  description = "Storage size in MB"
  type        = number
  default     = 32768
}

variable "postgres_backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

variable "postgres_admin_username" {
  description = "PostgreSQL administrator login"
  type        = string
  default     = "pgadmin"
}

variable "postgres_admin_password" {
  description = "PostgreSQL administrator password (override via TF_VAR_postgres_admin_password)"
  type        = string
  default     = "cw5*6KZ+d1G=7HSy"
  sensitive   = true
}

variable "postgres_database_name" {
  description = "Default database name"
  type        = string
  default     = "appdb"
}

variable "acr_name" {
  description = "Globally unique Container Registry name"
  type        = string
  default     = "myprojectacr"
}

variable "acr_sku" {
  description = "ACR SKU tier (Basic, Standard, Premium)"
  type        = string
  default     = "Standard"
}

variable "acr_admin_enabled" {
  description = "Enable admin user on registry"
  type        = bool
  default     = false
}

variable "acr_zone_redundancy_enabled" {
  description = "Enable zone redundancy on ACR (requires Premium SKU)"
  type        = bool
  default     = false
}

variable "key_vault_name" {
  description = "Globally unique Key Vault name"
  type        = string
  default     = "myprojectkv"
}

variable "key_vault_sku" {
  description = "Key Vault SKU (standard or premium)"
  type        = string
  default     = "standard"
}
