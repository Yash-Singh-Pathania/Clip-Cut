# This script stops, deletes, and restarts Minikube, then runs another script to apply Kubernetes manifests.

Write-Host "Stopping Minikube..." -ForegroundColor Yellow
minikube stop

Write-Host "Deleting Minikube..." -ForegroundColor Yellow
minikube delete

Write-Host "Starting Minikube..." -ForegroundColor Yellow
minikube start

Write-Host "Running apply_all_k8s.ps1 to apply manifests..." -ForegroundColor Yellow
# Ensure the script path is correctly specified if it's not in the current directory
$scriptPath = ".\apply_all_k8s.ps1"
if (Test-Path $scriptPath) {
    . $scriptPath
} else {
    Write-Host "Error: apply_all_k8s.ps1 not found at $scriptPath" -ForegroundColor Red
}

Write-Host "Starting Minikube tunnel..." -ForegroundColor Yellow
minikube tunnel