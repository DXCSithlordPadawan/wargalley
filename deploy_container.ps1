Write-Host "Deploying War Galley inside a container..."
New-Item -ItemType Directory -Force -Path assets   | Out-Null
New-Item -ItemType Directory -Force -Path analytics | Out-Null

# Try podman-compose first, fall back to docker compose
if (Get-Command podman-compose -ErrorAction SilentlyContinue) {
    Write-Host "Using podman-compose..."
    podman-compose up -d
} elseif (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Using docker compose..."
    docker compose up -d
} else {
    Write-Host "Error: neither podman-compose nor docker compose was found." -ForegroundColor Red
    Write-Host "Install Podman Desktop (https://podman-desktop.io/) or Docker Desktop (https://www.docker.com/products/docker-desktop/)."
    exit 1
}

Write-Host "Server live at http://localhost:5000"
