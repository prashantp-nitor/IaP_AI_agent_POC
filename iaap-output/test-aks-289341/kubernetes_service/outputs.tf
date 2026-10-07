output "cluster_name" {
  value = module.aks.name
}

output "cluster_id" {
  value = module.aks.resource_id
}
