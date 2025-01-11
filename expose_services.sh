#!/bin/bash

# This script updates Kubernetes services to expose specific ports,
# sets up port forwarding for multiple services,
# and prints the URLs for accessing them locally.

# Define the desired node ports for patching services (optional for port-forwarding)
FRONTEND_NODE_PORT=31001
USER_SERVICE_LB_PORT=31002
VIDEO_UPLOAD_LB_PORT=31003
MONITORING_LB_PORT=31004
POSTGRES_NODE_PORT=31005
MONGODB_NODE_PORT=31006

# Patch services to update their types and ports (optional step)
kubectl patch svc fronted-service -p "{\"spec\": {\"type\": \"NodePort\", \"ports\": [{\"port\": 8005, \"nodePort\": $FRONTEND_NODE_PORT}]}}"
kubectl patch svc user-service -p "{\"spec\": {\"type\": \"LoadBalancer\", \"ports\": [{\"port\": 80, \"nodePort\": $USER_SERVICE_LB_PORT}]}}"
kubectl patch svc video-upload-service -p "{\"spec\": {\"type\": \"LoadBalancer\", \"ports\": [{\"port\": 81, \"nodePort\": $VIDEO_UPLOAD_LB_PORT}]}}"
kubectl patch svc monitoring-service -p "{\"spec\": {\"type\": \"LoadBalancer\", \"ports\": [{\"port\": 80, \"nodePort\": $MONITORING_LB_PORT}]}}"
kubectl patch svc postgres-service -p "{\"spec\": {\"type\": \"NodePort\", \"ports\": [{\"port\": 5432, \"nodePort\": $POSTGRES_NODE_PORT}]}}"
kubectl patch svc mongodb-service -p "{\"spec\": {\"type\": \"NodePort\", \"ports\": [{\"port\": 27017, \"nodePort\": $MONGODB_NODE_PORT}]}}"

echo "Services updated successfully!"

# Start port forwarding for all specified services in the background
kubectl port-forward service/frontend-service 8005:8005 &
kubectl port-forward service/user-service 8080:80 &
kubectl port-forward service/video-upload-service 8081:81 &
kubectl port-forward service/monitoring-service 8082:80 &
kubectl port-forward service/postgres-service 5432:5432 &
kubectl port-forward service/mongodb-service 27017:27017 &

echo "Port forwarding initiated for all services."

# Print out local access URLs
echo "Access the services locally using the following URLs/ports:"
echo " - frontend-service: http://localhost:8005"
echo " - user-service: http://localhost:8080"
echo " - video-upload-service: http://localhost:8081"
echo " - monitoring-service: http://localhost:8082"
echo " - postgres-service: accessible via localhost:5432"
echo " - mongodb-service: accessible via localhost:27017"

# Keep the script alive to maintain port-forwarding in the foreground (optional):
# Uncomment the following line if you want the script to wait and not exit immediately:
# read -p "Press enter to exit and stop port forwarding..."
