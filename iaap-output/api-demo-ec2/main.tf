module "ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 5.0"

  name = var.instance_name
  ami = var.ami_id
  instance_type = var.instance_type
  associate_public_ip_address = true
  monitoring = true
  root_block_device = [
    {
      volume_size = 20
      volume_type = "gp3"
      encrypted = true
    },
  ]
  tags = merge({
    ManagedBy = "IAAP"
    environment = "dev"
    owner = "admin@example.com"
    project = "iaap"
  }, var.extra_tags)
  key_name = "daas-test"
}
