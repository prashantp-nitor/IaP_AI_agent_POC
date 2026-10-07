output "server_name" {
  value = module.postgresql.name
}

output "server_id" {
  value = module.postgresql.resource_id
}

output "fqdn" {
  value = module.postgresql.fqdn
}
