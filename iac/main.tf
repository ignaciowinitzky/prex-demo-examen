terraform {
  required_version = ">= 1.0.0, <=1.5.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.32"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }
  }
}

provider "aws" {
  region = var.region
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

locals {
  default_tags = {
    environment = var.environment
    project     = var.project_name
    product     = var.product
    region      = var.region
  }
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
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name                    = var.project_name
  cluster_version                 = var.cluster_version
  cluster_endpoint_public_access  = var.cluster_endpoint_public_access
  cluster_endpoint_private_access = var.cluster_endpoint_private_access
  vpc_id                          = module.vpc.vpc_id
  subnet_ids                      = module.vpc.private_subnets
  enable_irsa                     = var.enable_irsa
  tags                            = local.default_tags
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

module "eks_aws_auth" {
  source                    = "terraform-aws-modules/eks/aws//modules/aws-auth"
  version                   = "~> 20.0"
  manage_aws_auth_configmap = true
  aws_auth_users            = var.aws_auth_users
  depends_on                = [module.eks]
}

resource "aws_iam_policy" "aws_lb_controller" {
  name        = "${var.project_name}-aws-lb-controller"
  description = "IAM policy for AWS Load Balancer Controller"
  policy      = file("${path.module}/policies/aws-load-balancer-controller.json")
  tags        = local.default_tags
}

module "aws_lb_controller_irsa" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version   = ">= 5.30, < 6.0"
  role_name = "${var.project_name}-aws-lb-controller"
  tags      = local.default_tags
  role_policy_arns = {
    aws_lb_controller = aws_iam_policy.aws_lb_controller.arn
  }
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
}
