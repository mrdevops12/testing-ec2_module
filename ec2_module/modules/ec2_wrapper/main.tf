data "aws_subnet" "selected" {
  id = var.subnet_id
}

locals {
  required_tags = [
    "AppServiceName", "AppServiceID", "ApplicationDesc", "Description",
    "Environment", "Iac", "IaC_By", "TimeStamp", "DataType",
    "Created_By", "TierID", "ApplicationOwner", "CostCenter"
  ]

  missing_tags = [for tag in local.required_tags : tag if !contains(keys(var.tags), tag)]

  validated_tags = length(local.missing_tags) == 0 ? var.tags : (
    throw("Missing required tag(s): ${join(", ", local.missing_tags)}")
  )
}

resource "aws_instance" "ec2_instance" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = var.security_group_ids
  associate_public_ip_address = var.associate_public_ip
  key_name                    = var.key_name

  root_block_device {
    volume_size = var.root_volume_size
    volume_type = "gp3"
  }

  tags = merge(local.validated_tags, {
    Name = var.name
  })
}

resource "aws_ebs_volume" "data" {
  count             = var.ebs_volume_count
  availability_zone = data.aws_subnet.selected.availability_zone
  size              = var.ebs_volume_size
  type              = "gp3"

  tags = merge(var.tags, {
    Name = "${var.name}-data-${count.index + 1}"
  })
}

resource "aws_volume_attachment" "data_attach" {
  count       = var.ebs_volume_count
  device_name = "/dev/sd${element(["f", "g", "h", "i", "j"], count.index)}"
  volume_id   = aws_ebs_volume.data[count.index].id
  instance_id = aws_instance.ec2_instance.id
}
