
variable "ami_id" {
  type        = string
  description = "AMI ID to launch the EC2 instance"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type (e.g., t2.micro)"
}

variable "subnet_id" {
  type        = string
  description = "Subnet ID to launch the instance into"
}

variable "security_group_ids" {
  type        = list(string)
  description = "List of security group IDs"
}

variable "associate_public_ip" {
  type        = bool
  description = "Whether to associate a public IP"
}

variable "key_name" {
  type        = string
  description = "SSH key pair name"
}

variable "tags" {
  type        = map(string)
  description = "Common tags to apply"
}

variable "name" {
  type        = string
  description = "EC2 instance name"
}

variable "ebs_volume_count" {
  type        = number
  description = "Number of EBS volumes to attach"
  default     = 2
}

variable "ebs_volume_size" {
  type        = number
  description = "Size of each EBS volume in GB"
  default     = 10
}

variable "root_volume_size" {
  type        = number
  description = "Root volume size in GB"
  default     = 8
}
