
ami_id               = "ami-0953476d60561c955"
instance_type        = "t3.nano"
key_name             = "kira"
private_subnet_ids   = ["subnet-0ab750440176b8ab0", "subnet-05cfbfc5a95afa918", "subnet-09077b47a5a872037"]
security_group_ids   = ["sg-03dea883f0cc3e9f3"]
associate_public_ip  = false

tags = {
  Environment = "dev"
  Owner       = "mahesh"
}

name = "ha-ec2"
ebs_volume_count = 2
ebs_volume_size  = 10
root_volume_size = 8
