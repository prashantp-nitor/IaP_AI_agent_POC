# ── VPC ──
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"
  azs = ["${var.region}a", "${var.region}b"]
  private_subnets = [
    "10.0.1.0/24",
    "10.0.2.0/24",
  ]
  public_subnets = [
    "10.0.101.0/24",
    "10.0.102.0/24",
  ]
  enable_nat_gateway = true
  single_nat_gateway = true
  enable_dns_hostnames = true
  public_subnet_tags = {
    kubernetes.io/role/elb = 1
  }
  private_subnet_tags = {
    kubernetes.io/role/internal-elb = 1
  }
  tags = merge({
    ManagedBy = "IAAP"
    environment = "dev"
    owner = "admin@example.com"
    project = "fitcart-test"
  }, var.extra_tags)
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name = var.cluster_name
  cluster_version = var.kubernetes_version
  cluster_endpoint_public_access = true
  cluster_endpoint_private_access = true
  vpc_id = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  eks_managed_node_groups = {
    default = {
      instance_types = [var.node_instance_type]
      min_size = 1
      max_size = var.node_count * 2
      desired_size = var.node_count
    }
  }
  tags = merge({
    ManagedBy = "IAAP"
    environment = "dev"
    owner = "admin@example.com"
    project = "fitcart-test"
  }, var.extra_tags)
}
