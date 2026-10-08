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

variable "account_name" {
  description = "Globally unique storage account name"
  type        = string
  default     = "storagetest"
}

variable "account_tier" {
  description = "Performance tier (Standard or Premium)"
  type        = string
  default     = "Standard"
}

variable "replication" {
  description = "Replication type (LRS, ZRS, GRS, RAGRS)"
  type        = string
  default     = "LRS"
}

variable "access_tier" {
  description = "Blob access tier (Hot or Cool)"
  type        = string
  default     = "Hot"
}

variable "extra_tags" {
  description = "Additional tags applied to all resources"
  type        = map(string)
  default     = {}
}
