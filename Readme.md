<a href="https://github.com/jdav-freiburg/depot-manager-backend/actions/workflows/publish_docker.yml">
    <img src="https://github.com/jdav-freiburg/depot-manager-backend/actions/workflows/publish_docker.yml/badge.svg" />
</a>
<img src="https://img.shields.io/github/license/jdav-freiburg/depot-manager-backend.svg" alt="License" />

# Server for Depot Manager

This is the backend for [depot-manager-frontend](https://github.com/jdav-freiburg/depot-manager-frontend/tree/develop).
See [depot-manager-frontend](https://github.com/jdav-freiburg/depot-manager-frontend/tree/develop) for more documentation.

## Development server and developing
1. Install [UV](https://docs.astral.sh/uv/getting-started/installation/).
2. Install all dependencies + development dependencies: `uv sync --locked`
3. Generate the db schema
```
uv run python -c $'import asyncio
from tortoise import Tortoise

async def main():
    await Tortoise.init(
        db_url=f"sqlite://devdepot.sqlite",
        modules={"depot": ["depot_server.db2.models"]},
        )
    await Tortoise.generate_schemas()
    print("Init done")

asyncio.run(main())'
```
4. Run `uv run uvicorn depot_server.api:app` for a dev server.

> [!INFO]  
> Run with `NO_AUTH=1` environment variable to turn off the authentication logic

If you're using VSCode, run the `API no auth` target for local development and 
disabled authentication logic.

You can also use [just](https://just.systems/man/en/) to run some targets.
The most simple one is `just run` which starts the backend unauthenticated.
To see all just targets run `just -l`

## Altering the data model

## Versioning
This project uses semantic versioning as defined [here](https://semver.org/).
To bump the version, either edit the version in `pyproject.toml` or use 
`uv version --bump <major, minor, patch>`

## Deployment server

Use a ASGI server and run the `depot_server.api:app` module.

### Todo
- [ ] add meta to each model, to keep table name disconnected from model name,
        see [here](https://tortoise.github.io/models.html#the-meta-class)
- [ ] Add validators
- [ ] same formatting everywhere
- [ ] history model
- [ ] define useful indices, see above link