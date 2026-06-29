module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = var.db_identifier
  engine = var.engine
  engine_version = var.engine_version
  family = var.db_family
  major_engine_version = var.major_engine_version
  instance_class = var.instance_class
  allocated_storage = var.allocated_storage
  username = var.db_username
  manage_master_user_password = false
  password = var.db_password
  port = 3306
  storage_encrypted = true
  publicly_accessible = false
  multi_az = false
  skip_final_snapshot = true
  tags = merge({
    ManagedBy = "IAAP"
    environment = "dev"
    owner = "admin@example.com"
    project = "iaap"
  }, var.extra_tags)
}
