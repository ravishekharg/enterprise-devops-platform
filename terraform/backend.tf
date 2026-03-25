terraform {
  backend "s3" {
    bucket         = "enterprise-devops-tf-state"
    key            = "platform/eks/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
  }
}