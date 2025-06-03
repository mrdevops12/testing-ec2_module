ami_id               = "ami-0953476d60561c955"
instance_type        = "t3.nano"
key_name             = "kira"
private_subnet_ids   = ["subnet-0ab750440176b8ab0", "subnet-05cfbfc5a95afa918", "subnet-09077b47a5a872037"]
security_group_ids   = ["sg-03dea883f0cc3e9f3"]
associate_public_ip  = false

tags = {
  AppServiceName    = "MyApp"
  AppServiceID      = "APP123"
  ApplicationDesc   = "App EC2 Module"
  Description       = "Provision EC2 via module"
  Environment       = "dev"
  Iac               = "Terraform"
  IaC_By            = "DevSecOps"
  TimeStamp         = "06022025"
  DataType          = "PII"
  Created_By        = "john.d_doe"
  TierID            = "Tier1"
  ApplicationOwner  = "john.d_doe"
  CostCenter        = "CC1001"
}

name = "ha-ec2"
ebs_volume_count = 2
ebs_volume_size  = 10
root_volume_size = 8
