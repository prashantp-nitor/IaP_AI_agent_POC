output "elasticache_cluster_arn" {
  value = module.elasticache.cluster_arn
}

output "elasticache_cache_nodes" {
  value = module.elasticache.cluster_cache_nodes
}

output "elasticache_engine_version" {
  value = module.elasticache.cluster_engine_version_actual
}
