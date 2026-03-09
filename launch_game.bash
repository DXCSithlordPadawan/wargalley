#!/bin/bash
# Usage:
#   ./launch_game.bash            — run the server directly with Python (default)
#   ./launch_game.bash --container — build and run inside a Podman/Docker container

echo "Initializing War Galley Digital Engine..."
mkdir -p assets analytics

if [[ "$1" == "--container" ]]; then
    echo "Deployment mode: container"
    if command -v podman-compose &>/dev/null; then
        podman-compose up -d
    elif command -v docker &>/dev/null; then
        docker compose up -d
    else
        echo "Error: neither podman-compose nor docker compose found. Install one to use --container mode." >&2
        exit 1
    fi
    echo "Server live at http://localhost:5000"
    echo ""
    echo "To connect as a client, open a second terminal and run:"
    echo "  python3 src/client.py"
    echo ""
else
    echo "Deployment mode: native Python"
    python3 src/asset_gen.py
    echo "Server starting at http://localhost:5000"
    echo ""
    echo "Once the server is ready, open a second terminal and run:"
    echo "  python3 src/client.py"
    echo ""
    python3 src/server.py
fi
