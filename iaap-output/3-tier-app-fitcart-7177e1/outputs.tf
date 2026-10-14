output "resource_group_name" {
  description = "Name of the resource group"
  value       = data.azurerm_resource_group.rg.name
}

output "location" {
  description = "Azure region"
  value       = var.region
}

output "vnet_id" {
  description = "Virtual Network ID"
  value       = module.vnet.resource_id
}

output "vnet_name" {
  description = "Virtual Network Name"
  value       = module.vnet.name
}

output "acr_login_server" {
  description = "ACR login server endpoint"
  value       = module.acr.login_server
}

output "acr_id" {
  description = "ACR resource ID"
  value       = module.acr.resource_id
}
