output "instance_id" {
  description = "ID of the created EC2 instance"
  value       = aws_instance.ec2_instance.id
}

output "private_ip" {
  description = "Private IP of the instance"
  value       = aws_instance.ec2_instance.private_ip
}
