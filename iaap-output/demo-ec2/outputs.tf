output "instance_id" {
  value = module.ec2_instance.id
}

output "instance_arn" {
  value = module.ec2_instance.arn
}

output "instance_name" {
  value = var.instance_name
}

output "instance_type" {
  value = module.ec2_instance.instance_type
}

output "availability_zone" {
  value = module.ec2_instance.availability_zone
}

output "private_ip" {
  value = module.ec2_instance.private_ip
}

output "public_ip" {
  value = module.ec2_instance.public_ip
}

output "private_dns" {
  value = module.ec2_instance.private_dns
}

output "public_dns" {
  value = module.ec2_instance.public_dns
}

output "subnet_id" {
  value = module.ec2_instance.subnet_id
}

output "vpc_id" {
  value = data.aws_vpc.default.id
}

output "security_group_ids" {
  value = module.ec2_instance.vpc_security_group_ids
}

output "iam_instance_profile" {
  value = module.ec2_instance.iam_instance_profile
}
