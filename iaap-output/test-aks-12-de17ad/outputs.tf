output "resource_group_name" {
  description = "Name of the resource group"
  value       = data.azurerm_resource_group.rg.name
}

output "location" {
  description = "Azure region"
  value       = var.region
}

output "cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.name
}

output "cluster_id" {
  description = "ID of the AKS cluster"
  value       = module.aks.resource_id
}
