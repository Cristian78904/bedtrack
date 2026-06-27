# BedTrack - Infraestructura como Código con Terraform

provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "bedtrack" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "bedtrack-vpc"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "bedtrack" {
  name     = "bedtrack-cluster"
  role_arn = aws_iam_role.eks.arn
  
  vpc_config {
    subnet_ids = aws_subnet.bedtrack[*].id
  }
}

# RDS SQL Server
resource "aws_db_instance" "bedtrack" {
  engine         = "sqlserver-ex"
  instance_class = "db.t3.large"
  allocated_storage = 100
  storage_encrypted = true
  backup_retention_period = 7
  
  db_name  = "bedtrack"
  username = "admin"
  password = var.db_password
}

# Read Replica
resource "aws_db_instance" "bedtrack_replica" {
  engine         = "sqlserver-ex"
  instance_class = "db.t3.large"
  allocated_storage = 100
  
  replicate_source_db = aws_db_instance.bedtrack.id
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "bedtrack-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 3
  parameter_group_name = "default.redis6.x"
}

output "eks_cluster_endpoint" {
  value = aws_eks_cluster.bedtrack.endpoint
}

output "db_endpoint" {
  value = aws_db_instance.bedtrack.endpoint
}
