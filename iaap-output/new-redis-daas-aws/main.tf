module "elasticache" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "~> 1.4"

  cluster_id = var.cluster_id
  create_cluster = true
  create_replication_group = false
  engine = "redis"
  engine_version = var.engine_version
  node_type = var.node_type
  num_cache_nodes = 1
  port = var.port
  transit_encryption_enabled = true
  apply_immediately = true
  create_parameter_group = true
  parameter_group_family = var.parameter_group_family
  tags = merge({
    ManagedBy = "IAAP"
    environment = "dev"
    owner = "admin@example.com"
    project = "daas-test-project"
  }, var.extra_tags)
  create_subnet_group = false
}
