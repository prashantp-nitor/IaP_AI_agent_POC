output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_arn" {
  value = module.eks.cluster_arn
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_version" {
  value = module.eks.cluster_version
}

output "cluster_status" {
  value = module.eks.cluster_status
}

output "cluster_security_group_id" {
  value = module.eks.cluster_security_group_id
}

output "oidc_issuer" {
  value = try(module.eks.cluster_oidc_issuer_url, "")
}

output "node_group_name" {
  value = try(keys(module.eks.eks_managed_node_groups)[0], "")
}

output "node_role_arn" {
  value = try(module.eks.eks_managed_node_groups["default"].iam_role_arn, "")
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
