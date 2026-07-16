from uuid import UUID

from fastapi import APIRouter, HTTPException

from depot_server.db2.models.news import NewsEntry as DbNewsEntry
from depot_server.db2.repository.repo_news import NewsRepo
from depot_server.logic.announcement import announcement_from_orm
from .models.announcement import Announcement, AnnouncementPending

router = APIRouter()


@router.get("/announcement")
async def get_announcements() -> list[Announcement]:
    """Retrieve all announcements"""
    db_announcements = await NewsRepo.get_all_announcements()
    return [announcement_from_orm(announcement) for announcement in db_announcements]


@router.get("/announcement/{announcement_id}")
async def get_announcement(announcement_id: UUID) -> Announcement:
    """Retrieve a single announcement by id"""
    db_announcement = await NewsRepo.get_announcement_by_id(announcement_id)
    if not db_announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement_from_orm(db_announcement)


@router.post("/announcement")
async def create_announcement(announcement: AnnouncementPending) -> Announcement:
    """Create a new announcement"""
    author = "<user who made the request>"
    db_announcement = await NewsRepo.create_announcement(
        author=author,
        **announcement.model_dump())
    return announcement_from_orm(db_announcement)


@router.put("/announcement/{announcement_id}")
async def update_announcement(announcement_id: UUID, announcement: AnnouncementPending) -> Announcement:
    """Update an existing announcement"""
    db_announcement: DbNewsEntry = await NewsRepo.update_announcement(announcement_id, **announcement.model_dump())
    return announcement_from_orm(db_announcement)


@router.delete("/announcement/{announcement_id}")
async def delete_announcement(announcement_id: UUID) -> None:
    """Delete an announcement"""
    await NewsRepo.delete_announcement(announcement_id)
