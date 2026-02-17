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

3. Run `uv run uvicorn depot_server.api:app` for a dev server.

> [!NOTE]  
> Run with `NO_AUTH=1` environment variable to turn off the authentication logic

If you're using VSCode, run the `API no auth` target for local development and 
disabled authentication logic.

You can also use [just](https://just.systems/man/en/) to run some targets.
The most simple one is `just run` which starts the backend unauthenticated.
To see all just targets run `just -l`

## Commits
#### Commit Messages
Please adhere to the [conventional commits principle](https://www.conventionalcommits.org/en/v1.0.0/#summary).
This helps to have a better overview over what happenend on the branches, 
as well as to determine on which version the next release needs to get bumped.
The most important prefixes used are:
- `fix:` a  bugfix for the codebase (correlates to a bump of the PATCH version)
- `feat:` a new feature added to the codebase(correlates to a bump of the MINOR version)
Use a `!` to mark breaking changes requiring a bump of the MAJOR.

#### Squashing and linear commit history
Please squash your commits on your feature branch and rebase them against 
`origin/develop`. This enables us to do fast-forward merges on develop,
leading to a clean, easy to read, linear commit history.
To rebase you can either use tools like [Lazygit](https://github.com/jesseduffield/lazygit) or do it on the CLI:

1. Use `git log` to determine the amount of commits you did on yuor feature branch
2. Start an interactive rebase: `git rebase -i HEAD~<amount of commits>`
3. Set the first commit to `pick`, all others to `squash`
4. Edit your commit message (see previous paragraph)
5. Finish rebase
6. Rebase against origin develop, to place your changes on top of the existing ones:
    - `git fetch`
    - `git rebase origin/develop`
7. Push your changes, if you already had other commits you need to force push to the feature branch:
    `git push -f`

## Versioning
This project uses semantic versioning as defined [here](https://semver.org/).  
Bump versions only when doing a release!  
To bump the version, either edit the version in `pyproject.toml` or use 
`uv version --bump <major, minor, patch>`  


## Deployment server

Use a ASGI server and run on `depot_server.api:app`.
