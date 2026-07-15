module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = var.vpc_name
  cidr = var.cidr_block
  azs = ["${var.region}a"]
  public_subnets = [
    "10.0.1.0/24",
  ]
  private_subnets = [
    "10.0.2.0/24",
  ]
  enable_nat_gateway = true
  single_nat_gateway = true
  enable_dns_hostnames = true
  enable_dns_support = true
  tags = merge({
    ManagedBy = "IAAP"
  }, var.extra_tags)
}
