# Mintuu Infrastructure Provisioning
provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "mintuu_cluster" {
  name     = "mintuu-production"
  role_arn = aws_iam_role.eks_cluster_role.arn
  vpc_config {
    subnet_ids = aws_subnet.mintuu_subnets[*].id
  }
}
