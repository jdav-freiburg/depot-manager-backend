# Justfile for running the JDAV Backend

 
[doc('spawn test mongo db and launch application in hot reload mode with 
authentication bypassed. Useful for local development')]
run:
    docker compose up -d mongo
    - NO_AUTH=1 uv run uvicorn depot_server.api:app --reload
    docker compose down


[doc('spawn test mongo db and launch application in hot reload mode.
Uses auth as defined in settings. Useful for testing auth related features.')]
run_auth:
    docker compose run -d mongo
    uv run uvicorn depot_server.api:app --reload
    docker compose down

# launches a mongo db in background
db:
    docker compose up -d mongo
