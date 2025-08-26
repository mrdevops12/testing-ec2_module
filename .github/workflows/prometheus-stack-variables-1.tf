variable "prometheus_chart_repo" {
  description = "Private OCI repo for Prometheus chart"
  type        = string
}

variable "prometheus_chart_version" {
  description = "Version of Prometheus Helm chart"
  type        = string
}
