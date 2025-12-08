terraform {
  required_version = ">= 1.0.0, <=1.5.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

locals {
  default_tags = {
    environment = var.environment
    project     = var.project_name
    product     = var.product
    region      = var.region
  }
}
data "http" "my_ip" {
  url = "https://checkip.amazonaws.com"
}

locals {
  my_public_ip = "${chomp(data.http.my_ip.response_body)}/32"
}

module "vpc" {
  source              = "terraform-aws-modules/vpc/aws"
  version             = "~> 5.0"
  name                = var.project_name
  cidr                = var.cidr
  azs                 = ["${var.region}a", "${var.region}b"]
  private_subnets     = var.private_subnets
  public_subnets      = var.public_subnets
  enable_nat_gateway  = var.enable_nat_gateway
  single_nat_gateway  = var.single_nat_gateway
  public_subnet_tags  = local.default_tags
  private_subnet_tags = local.default_tags
  tags                = local.default_tags
}

module "eks" {
  source                                   = "terraform-aws-modules/eks/aws"
  version                                  = "~> 20.0"
  cluster_name                             = var.project_name
  cluster_version                          = var.cluster_version
  cluster_endpoint_public_access           = var.cluster_endpoint_public_access
  cluster_endpoint_private_access          = var.cluster_endpoint_private_access
  vpc_id                                   = module.vpc.vpc_id
  subnet_ids                               = module.vpc.private_subnets
  enable_irsa                              = var.enable_irsa
  tags                                     = local.default_tags
  enable_cluster_creator_admin_permissions = true

  cluster_enabled_log_types = [
    "api",
    "audit",
    "authenticator",
    "controllerManager",
    "scheduler"
  ]
  cluster_encryption_config = {
    resources = ["secrets"]
  }
  eks_managed_node_groups = {
    default = {
      min_size       = var.min_size
      max_size       = var.max_size
      desired_size   = var.desired_size
      instance_types = var.instance_types
      subnets        = module.vpc.private_subnets
      tags           = local.default_tags
    }
  }
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }
}

resource "aws_security_group_rule" "allow_all_from_my_ip_to_eks" {
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = [local.my_public_ip]
  security_group_id = module.eks.cluster_security_group_id
  description       = "Allow ALL traffic from my public IP only"
}
