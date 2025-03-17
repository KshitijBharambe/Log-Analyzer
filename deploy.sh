!bin/bash

# Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Create config and storage
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/persistent-volumes.yaml

# Deploy core components
kubectl apply -f kubernetes/elasticsearch-kibana.yaml
kubectl apply -f kubernetes/kafka-zookeeper.yaml
kubectl apply -f kubernetes/grafana.yaml

# Deploy log processing components
kubectl apply -f kubernetes/logging-components.yaml

# Create ingress (if needed)
kubectl apply -f kubernetes/ingress.yaml