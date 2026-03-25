
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "enterprise-platform-vpc"
  cidr = "10.10.0.0/16"

  azs             = ["ap-south-1a","ap-south-1b","ap-south-1c"]
  private_subnets = ["10.10.1.0/24","10.10.2.0/24","10.10.3.0/24"]
  public_subnets  = ["10.10.4.0/24","10.10.5.0/24","10.10.6.0/24"]

  enable_nat_gateway = True
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.0.0"

  cluster_name    = "enterprise-platform-cluster"
  cluster_version = "1.29"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  enable_irsa = True

  eks_managed_node_groups = {
    default = {
      desired_capacity = 6
      min_capacity     = 3
      max_capacity     = 9
      instance_types   = ["t3.medium"]
    }
  }
}
