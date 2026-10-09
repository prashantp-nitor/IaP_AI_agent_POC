output "vnet_name" {
  value = module.vnet.name
}

output "vnet_id" {
  value = module.vnet.resource_id
}

output "address_space" {
  value = module.vnet.address_spaces
}

output "subnets" {
  value = module.vnet.subnets
}

output "resource_group_name" {
  value = var.resource_group_name
}

output "location" {
  value = var.region
}
