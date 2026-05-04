#!/bin/bash
# Script de déploiement unifié
echo "🚀 Nettoyage du cluster..."
sudo k3s kubectl delete --all pods,services,deployments,configmaps
echo "📦 Déploiement de la stack AIOps..."
sudo k3s kubectl apply -f elasticsearch.yaml
sudo k3s kubectl apply -f kibana.yaml
sudo k3s kubectl apply -f prometheus.yaml
sudo k3s kubectl apply -f otel-collector.yaml
echo "✅ Déploiement terminé. Vérifiez avec 'sudo k3s kubectl get pods'"