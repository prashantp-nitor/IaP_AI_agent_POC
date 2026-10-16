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

output "cluster_name" {
  description = "Name of the AKS cluster"
  value       = module.aks.name
}

output "cluster_id" {
  description = "ID of the AKS cluster"
  value       = module.aks.resource_id
}

output "fqdn" {
  description = "Fully qualified domain name of the PostgreSQL server"
  value       = module.postgres.fqdn
}

output "port" {
  description = "Database port"
  value       = "5432"
}

output "database_name" {
  description = "Default database name"
  value       = var.postgres_database_name
}

output "administrator_login" {
  description = "PostgreSQL administrator username"
  value       = var.postgres_admin_username
}

output "acr_login_server" {
  description = "ACR login server endpoint"
  value       = module.acr.login_server
}

output "acr_id" {
  description = "ACR resource ID"
  value       = module.acr.resource_id
}

output "key_vault_uri" {
  description = "Key Vault URI"
  value       = module.key_vault.uri
}

output "key_vault_id" {
  description = "Key Vault resource ID"
  value       = module.key_vault.resource_id
}

output "storage_account_name" {
  description = "Storage Account Name"
  value       = module.storage.name
}

output "storage_account_id" {
  description = "Storage Account Resource ID"
  value       = module.storage.resource_id
}
