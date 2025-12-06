project_name = "demo"
product      = "demo"
aws_auth_users = [
  {
    userarn  = "arn:aws:iam::058264225985:user/ignacio@koibanx.com"
    username = "ignacio@koibanx.com"
    groups   = ["system:masters"]
  }
]
