module "ec2" {
  source  = "terraform-aws-modules/ec2-instance/aws"
  version = "~> 5.0"

  name = var.instance_name
  ami = var.ami_id
  instance_type = var.instance_type
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
  user_data = "#!/bin/bash
# Update and install Docker
dnf update -y
dnf install -y docker
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# Install Docker Compose
curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Ensure SSM agent is running
systemctl start amazon-ssm-agent
systemctl enable amazon-ssm-agent
"
  key_name = "daas-test"
}
