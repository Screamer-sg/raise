# Raisecom Configurator v6.2

Raisecom Configurator v6.2 is an offline-first toolkit for composing, validating and exporting configuration bundles for Raisecom switches. The solution ships with a FastAPI backend and a React + TailwindCSS frontend.

## Features

- JSON model catalogue describing supported Raisecom switch families.
- Smart validation for duplicate ports, VLAN ranges and QinQ setups.
- Automatic CLI/config file generation with instant preview.
- Profile backup/restore with encrypted credential storage and audit trail.
- Docker Compose stack for rapid local development.

## Getting started

```bash
# Start the full stack
docker compose up --build

# Run backend unit tests
cd backend
poetry install
pytest
```

The frontend development server listens on <http://localhost:5173> and proxies API calls to the backend running on <http://localhost:8000>.
