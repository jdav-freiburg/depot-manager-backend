from fastapi import APIRouter
from depot_server.version import version as version_, commit_hash


router = APIRouter()

@router.get("/version")
async def version() -> dict[str, str]:
    return {"version": version_, "commit_hash": commit_hash}
