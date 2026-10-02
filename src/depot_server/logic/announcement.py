from depot_server.api2.models.announcement import APIAnnouncement
from depot_server.db2.models.news import NewsEntry


def announcement_from_orm(entry: NewsEntry) -> APIAnnouncement:
    a = APIAnnouncement(
        id=entry.pk,
        author=entry.author,
        timestamp=entry.timestamp,
        title=entry.title,
        text=entry.text,
        expires=entry.expires,
        is_visible=entry.is_visible,
        is_pinned=entry.is_pinned
    )
    return a
