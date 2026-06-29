output "replication_group_primary_endpoint_address" {
  value = module.redis.replication_group_primary_endpoint_address
}

output "replication_group_reader_endpoint_address" {
  value = module.redis.replication_group_reader_endpoint_address
}

output "replication_group_id" {
  value = module.redis.replication_group_id
}

output "replication_group_arn" {
  value = module.redis.replication_group_arn
}
