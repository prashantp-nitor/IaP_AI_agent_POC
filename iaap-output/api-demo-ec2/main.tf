data "aws_vpc" "default" {
  default = true
}
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 5.0"

  name = var.instance_name
  ami = var.ami_id
  instance_type = var.instance_type
  subnet_id = data.aws_subnets.default.ids[0]
  monitoring = true
  root_block_device = [
    {
      volume_size = 20
      volume_type = "gp3"
      encrypted = false
    },
  ]
  tags = merge({
    ManagedBy = "IAAP"
    environment = "dev"
    owner = "admin@example.com"
    project = "iaap"
  }, var.extra_tags)
  user_data = <<-EOT
#!/bin/bash
# Ensure SSM agent is running
systemctl start amazon-ssm-agent
systemctl enable amazon-ssm-agent
EOT
  key_name = "daas-test"
}
