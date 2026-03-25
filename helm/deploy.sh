
#!/bin/bash

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts

helm upgrade --install mysql bitnami/mysql
helm upgrade --install keycloak bitnami/keycloak
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack
