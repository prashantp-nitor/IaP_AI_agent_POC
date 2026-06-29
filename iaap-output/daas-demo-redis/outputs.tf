output "primary_endpoint_address" {
  value = module.redis.primary_endpoint_address
}

output "reader_endpoint_address" {
  value = module.redis.reader_endpoint_address
}

output "port" {
  value = module.redis.port
}

output "replication_group_id" {
  value = module.redis.replication_group_id
}
