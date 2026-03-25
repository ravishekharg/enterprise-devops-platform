
# Enterprise DevOps Platform (End-to-End)

Architecture:

Terraform → EKS Cluster
Helm → Platform Services Deployment
GitHub Actions → CI/CD Automation
Python → Backup Automation
Python → Cluster Monitoring

Components:

EKS cluster provisioning
Helm deployment for MySQL, Keycloak, Prometheus, Grafana
GitHub Actions automation pipeline
Database backup scheduler
Cluster health monitoring toolkit

Usage:

terraform init
terraform apply

kubectl get nodes

bash helm/deploy.sh

python backup/backup.py

python monitoring/cluster_monitor.py
