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
    job_id = "342fb5d9-762a-4842-a1c3-5cd840651a28"
    project_folder = "3-tier-app-fitcart-342fb5"
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

variable "acr_name" {
  description = "Globally unique Container Registry name"
  type        = string
  default     = "3tierappfitcartacr342fb5"
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
