module "redis" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "~> 1.0"

  replication_group_id = var.cluster_id
  description = "Managed by IAAP"
  node_type = var.node_type
  num_cache_clusters = var.num_cache_nodes
  automatic_failover_enabled = var.automatic_failover_enabled
  multi_az_enabled = var.multi_az_enabled
  port = var.port
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  tags = merge({
    ManagedBy = "IAAP"
    environment = "dev"
    owner = "admin@example.com"
    project = "sample-daas-project"
  }, var.extra_tags)
}
