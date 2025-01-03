#!/bin/bash

# Check if service name was passed as an argument
if [ -z "$1" ]; then
  echo "Please provide the service name as an argument."
  exit 1
fi

SERVICE_NAME=$1

# Navigate to the service's Kubernetes folder
cd "${SERVICE_NAME}/k8s" || exit

# Extract the current image version from the deployment.yaml
CURRENT_IMAGE=$(grep 'image:' deployment.yaml | awk '{print $2}')
echo "Current image: $CURRENT_IMAGE"

# Break down the image name and version
IMAGE_NAME=$(echo "$CURRENT_IMAGE" | cut -d':' -f1)
CURRENT_VERSION=$(echo "$CURRENT_IMAGE" | cut -d':' -f2)

# Calculate the new version number
NEW_VERSION_NUMBER=$(echo "$CURRENT_VERSION" | awk -F. '{print $1 "." $2+1}')
NEW_IMAGE="$IMAGE_NAME:$NEW_VERSION_NUMBER"
echo "New image will be: $NEW_IMAGE"

# Build the new Docker image
docker build -t "$NEW_IMAGE" ../..

# Push the new Docker image
docker push "$NEW_IMAGE"

# Update the deployment.yaml with the new image version
sed -i "s|$CURRENT_IMAGE|$NEW_IMAGE|g" deployment.yaml

# Navigate back to the root folder of the project
cd ../../..

# Apply Kubernetes configurations
chmod +x apply_all_k8s.sh
./apply_all_k8s.sh

echo "Deployment update process complete for $SERVICE_NAME."
