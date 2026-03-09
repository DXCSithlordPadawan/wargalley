@echo off
echo Deploying War Galley inside a container...
mkdir assets 2>nul
mkdir analytics 2>nul

REM Try podman-compose first, fall back to docker compose
where podman-compose >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo Using podman-compose...
    podman-compose up -d
) else (
    where docker >nul 2>&1
    if %ERRORLEVEL% == 0 (
        echo Using docker compose...
        docker compose up -d
    ) else (
        echo Error: neither podman-compose nor docker compose was found.
        echo Install Podman Desktop ^(https://podman-desktop.io/^) or Docker Desktop ^(https://www.docker.com/products/docker-desktop/^).
        exit /b 1
    )
)

echo Server live at http://localhost:5000
