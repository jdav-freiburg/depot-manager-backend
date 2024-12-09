<a href="https://github.com/jdav-freiburg/depot-manager-backend/actions/workflows/publish_docker.yml">
    <img src="https://github.com/jdav-freiburg/depot-manager-backend/actions/workflows/publish_docker.yml/badge.svg" />
</a>
<img src="https://img.shields.io/github/license/voegtlel/depot-manager-backend.svg" alt="License" />

# Server for Depot Manager

This is the backend for [depot-manager-frontend](https://github.com/voegtlel/depot-manager-frontend).
See [depot-manager-frontend](https://github.com/voegtlel/depot-manager-frontend) for more documentation.

## Development server

Run `python -m uvicorn depot_server.api:app` for a dev server.

## Deployment server

Use a ASGI server and run on `depot_server.api:app`.
