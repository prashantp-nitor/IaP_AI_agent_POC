data "aws_ami" "default" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

module "ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 5.0"

  name = var.instance_name
  ami = data.aws_ami.default.id
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
  }, var.extra_tags)
}
