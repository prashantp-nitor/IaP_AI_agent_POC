terraform {
  required_version = ">= 1.11.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.12"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "~> 2.4"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
    modtm = {
      source  = "azure/modtm"
      version = "~> 0.3"
    }
  }
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

# Shared Resource Group (Existing)
data "azurerm_resource_group" "rg" {
  name = var.resource_group_name
}
