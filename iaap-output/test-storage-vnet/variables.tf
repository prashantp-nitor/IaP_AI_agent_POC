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

variable "vnet_name" {
  description = "Name of the Azure Virtual Network"
  type        = string
  default     = "production-network"
}

variable "address_space" {
  description = "Address space (CIDR blocks) for the Virtual Network"
  type        = list(string)
  default     = [
    "10.0.0.0/16",
  ]
}

variable "subnet_prefix" {
  description = "CIDR prefix for the default subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}
