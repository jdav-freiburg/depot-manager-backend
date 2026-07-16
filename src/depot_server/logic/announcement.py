from depot_server.api2.models.announcement import Announcement
from depot_server.db2.models.news import NewsEntry


def announcement_from_orm(entry: NewsEntry) -> Announcement:
    a = Announcement(
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
