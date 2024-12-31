#!/usr/bin/env bash

# This script finds every directory named "k8s" and applies all YAMLs in those directories via kubectl.

for dir in $(find . -type d -name "k8s"); do
  echo "Applying manifests in directory: $dir"
  kubectl apply -f "$dir"
done
