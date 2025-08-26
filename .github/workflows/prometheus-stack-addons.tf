module "prometheus-stack" {
  source                  = "./modules/prometheus-stack"
  namespace               = "monitoring"
  prometheus_chart_repo   = var.prometheus_chart_repo
  prometheus_chart_version = var.prometheus_chart_version
}
