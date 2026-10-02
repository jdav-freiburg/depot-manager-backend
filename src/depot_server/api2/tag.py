from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from depot_server.db2.models.item.tag import Tag as DbTag
from depot_server.db2.repository.item.repo_tag import TagRepo
from depot_server.db2.repository.base import ItemNotFound
from .models.tag import APITag, APITagPending

router = APIRouter(tags=["V2_Tag"])


@router.get("/tag")
async def get_tags() -> list[APITag]:
    db_tags = await TagRepo.get_all_tags()
    return [APITag.model_validate(tag, from_attributes=True) for tag in db_tags]


@router.get("/tag/{tag_id}")
async def get_tag(tag_id: UUID) -> APITag:
    db_tag = await TagRepo.get_tag_by_id(tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return APITag.model_validate(db_tag, from_attributes=True)


@router.post("/tag")
async def create_tag(tag: APITagPending) -> APITag:
    db_tag = await TagRepo.create_tag(**tag.model_dump(), tag_id=uuid4())
    return APITag.model_validate(db_tag, from_attributes=True)


@router.put("/tag/{tag_id}")
async def update_tag(tag_id: UUID, tag: APITagPending) -> APITag:
    try:
        db_tag: DbTag = await TagRepo.update_tag(tag_id, **tag.model_dump())
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    return APITag.model_validate(db_tag, from_attributes=True)


@router.delete("/tag/{tag_id}")
async def delete_tag(tag_id: UUID) -> None:
    try:
        await TagRepo.delete_tag(tag_id)
    except ItemNotFound as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
