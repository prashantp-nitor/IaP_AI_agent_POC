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
