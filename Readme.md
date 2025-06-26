<a href="https://github.com/jdav-freiburg/depot-manager-backend/actions/workflows/publish_docker.yml">
    <img src="https://github.com/jdav-freiburg/depot-manager-backend/actions/workflows/publish_docker.yml/badge.svg" />
</a>
<img src="https://img.shields.io/github/license/voegtlel/depot-manager-backend.svg" alt="License" />

# Server for Depot Manager

This is the backend for [depot-manager-frontend](https://github.com/jdav-freiburg/depot-manager-frontend/tree/develop).
See [depot-manager-frontend](https://github.com/jdav-freiburg/depot-manager-frontend/tree/develop) for more documentation.

## Development server and developing
1. Install [poetry](https://python-poetry.org/docs/#installation).
2. Install all dependencies + development dependencies: `poetry install --with dev`
3. Run `poetry run python -m uvicorn depot_server.api:app` for a dev server.

> [!info]
> Run with `NO_AUTH=1` environment variable to turn off the authentication logic

If you're using VSCode, run the `API no auth` target for local development and 
disabled authentication logic.

## Deployment server

Use a ASGI server and run on `depot_server.api:app`.
