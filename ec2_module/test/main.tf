
module "ec2_instances" {
  source = "../modules/ec2_wrapper"
  for_each = toset(var.private_subnet_ids)

  ami_id               = var.ami_id
  instance_type        = var.instance_type
  subnet_id            = each.value
  security_group_ids   = var.security_group_ids
  associate_public_ip  = false
  key_name             = var.key_name
  tags                 = var.tags
  name                 = "ec2-${each.key}"
  ebs_volume_count     = 2
  ebs_volume_size      = 10
  root_volume_size     = 8
}
