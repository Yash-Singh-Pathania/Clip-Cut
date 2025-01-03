#!/usr/bin/env bash

# This script stops, deletes, and restarts Minikube, then runs another script to apply Kubernetes manifests.

echo "Stopping Minikube..."
minikube stop

echo "Deleting Minikube..."
minikube delete

echo "Starting Minikube..."
minikube config set cpus 4
minikube config set memory 3920
minikube start

# Path to the apply_all_k8s.sh script
SCRIPT_PATH="./apply_all_k8s.sh"

if [[ -f "$SCRIPT_PATH" ]]; then
    echo "Running apply_all_k8s.sh to apply manifests..."
    bash "$SCRIPT_PATH"
else
    echo "Error: apply_all_k8s.sh not found at $SCRIPT_PATH"
    exit 1
fi

echo "Starting Minikube tunnel..."
sudo minikube tunnel