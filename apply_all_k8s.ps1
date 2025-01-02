Get-ChildItem -Recurse -Directory -Filter "k8s" | ForEach-Object {
    $dir = $_.FullName
    Write-Host "Applying manifests in directory: $dir"
    kubectl apply -f $dir
}