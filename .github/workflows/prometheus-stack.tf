resource "helm_release" "prometheus_stack" {
  name       = "kube-prometheus-stack"
  namespace  = var.namespace
  repository = var.prometheus_chart_repo
  chart      = "kube-prometheus-stack"
  version    = var.prometheus_chart_version
  atomic     = true

  values = [
    file("${path.module}/arc-scrape-config.yaml")
  ]
}
