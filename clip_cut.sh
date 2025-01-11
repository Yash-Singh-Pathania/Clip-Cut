#!/bin/bash

function loader {
    local pid=$1
    local delay=0.2
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

echo "Starting Minikube..."
minikube start

echo "Deploying resources to Minikube..."
chmod +x apply_all_k8s.sh
./apply_all_k8s.sh

echo "Waiting for all pods to be ready..."
(kubectl wait --for=condition=ready pod --all --timeout=300s) &

loader $!

echo "All systems are go! Your application is spinning up..."

SERVICE_URL= $(minikube service frontend-service --url)


echo "Clip Cut is now live, accessible at: ${SERVICE_URL}"

echo "Here’s your service URL again, just in case: ${SERVICE_URL}"
