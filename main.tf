provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "vault_eks_cluster" {
  name     = "vault-eks-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = aws_subnet.vault_subnet[*].id
  }
}

resource "aws_iam_role" "eks_cluster_role" {
  name = "eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_role_attachment" {
  role       = aws_iam_role.eks_cluster_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role" "vault_iam_role" {
  name = "vault-iam-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "vault_iam_role_attachment" {
  role       = aws_iam_role.vault_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
}

resource "aws_s3_bucket" "vault_storage_bucket" {
  bucket = "vault-storage-bucket"
  acl    = "private"
}

resource "aws_subnet" "vault_subnet" {
  count = 2
  vpc_id     = aws_vpc.vault_vpc.id
  cidr_block = cidrsubnet(aws_vpc.vault_vpc.cidr_block, 8, count.index)
}

resource "aws_vpc" "vault_vpc" {
  cidr_block = "10.0.0.0/16"
}
