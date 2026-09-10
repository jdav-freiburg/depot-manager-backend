from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise

from depot_server.db2.models import Item, ItemGroup, Reservation, ReservationItemLink
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.models.common import ReservationImportance
from depot_server.logic.reservation import ReservationService


@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.mark.asyncio
async def test_get_reserved_amount_returns_peak_overlap(init_db):
    item_group = await ItemGroup.create(
        name="Test Group",
        description="Group description",
    )
    item = await Item.create(
        group=item_group,
        name="Test Item",
        lendable=True,
        psa_category=PsaCategory.NONE,
    )

    reservations = [
        (datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, tzinfo=timezone.utc), 2),
        (datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, tzinfo=timezone.utc), 3),
        (datetime(2026, 1, 2, tzinfo=timezone.utc), datetime(2026, 1, 2, tzinfo=timezone.utc), 4),
    ]
    for start, end, amount in reservations:
        reservation = await Reservation.create(
            id=uuid4(),
            name="Test Reservation",
            start=start,
            end=end,
            user=uuid4(),
            contact="test@example.com",
            reservation_importance=ReservationImportance.PRIVATE,
        )
        await ReservationItemLink.create(
            item=item,
            reservation=reservation,
            amount=amount,
        )

    assert await ReservationService.get_reserved_item_amount(
        item.id,
        datetime(2025, 12, 31, tzinfo=timezone.utc),
        datetime(2026, 1, 3, tzinfo=timezone.utc),
    ) == 5