from typing import List
from uuid import UUID

from authlib.oidc.core import UserInfo
from fastapi import APIRouter, Depends, Body, HTTPException, Response

from depot_server.api.models import Bay, BayInWrite
from depot_server.helper.auth import Authentication

router = APIRouter()


@router.get(
    '/bays',
    tags=['Bay'],
    response_model=List[Bay],
)
async def get_bays(
        _user: UserInfo = Depends(Authentication()),
) -> List[Bay]:
    return []


@router.get(
    '/bays/{bay_id}',
    tags=['Bay'],
    response_model=Bay,
)
async def get_bay(
        bay_id: UUID,
        _user: UserInfo = Depends(Authentication()),
) -> Bay:
    raise HTTPException(404)


@router.post(
    '/bays',
    tags=['Bay'],
    response_model=Bay,
    status_code=201,
)
async def create_bay(
        bay: BayInWrite = Body(...),
        _user: UserInfo = Depends(Authentication(require_admin=True)),
) -> None:
    raise HTTPException(404)

@router.put(
    '/bays/{bay_id}',
    tags=['Bay'],
    response_model=Bay,
)
async def update_bay(
        bay_id: UUID,
        bay: BayInWrite = Body(...),
        _user: UserInfo = Depends(Authentication(require_admin=True)),
) -> None:
    raise HTTPException(404)


@router.delete(
    '/bays/{bay_id}',
    tags=['Bay'],
    status_code=204,
    response_class=Response,
)
async def delete_bay(
        bay_id: UUID,
        _user: UserInfo = Depends(Authentication(require_admin=True)),
) -> None:
    raise HTTPException(404)
