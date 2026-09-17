from datetime import date
from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise

from depot_server.db2.models import (
    Item,
    ItemComposite,
    ItemGroup,
    Reservation,
    ReservationCompositeLink,
    ReservationItemLink,
)
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
    item = await Item.create(
        name="Test Item",
        lendable=True,
        psa_category=PsaCategory.NONE,
    )

    reservations = [
        (date(2026, 1, 1), date(2026, 1, 3), 2),
        (date(2026, 1, 1), date(2026, 1, 3), 3),
        (date(2026, 1, 3), date(2026, 1, 4), 4),
        (date(2026, 1, 4), date(2026, 1, 5), 1),
        (date(2026, 1, 7), date(2026, 1, 10), 8)
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
        date(2025, 12, 30),
        date(2025, 12, 31),
    ) == 0
    assert await ReservationService.get_reserved_item_amount(
        item.id,
        date(2026, 1, 1),
        date(2026, 1, 3)
    ) == 9
    assert await ReservationService.get_reserved_item_amount(
        item.id,
        date(2025, 12, 31),
        date(2026, 1, 2)
    ) == 5
    assert await ReservationService.get_reserved_item_amount(
        item.id,
        date(2026, 1, 3),
        date(2026, 1, 4)
    ) == 9
    assert await ReservationService.get_reserved_item_amount(
        item.id,
        date(2026, 1, 4),
        date(2026, 1, 5)
    ) == 5
    assert await ReservationService.get_reserved_item_amount(
        item.id,
        date(2026, 1, 6),
        date(2026, 1, 6)
    ) == 0
    assert await ReservationService.get_reserved_item_amount(
        item.id,
        date(2026, 1, 8),
        date(2026, 1, 8)
    ) == 8


@pytest.mark.asyncio
async def test_get_all_reservations_prefetches_links(init_db):
    item = await Item.create(
        name="Test Item",
        lendable=True,
        psa_category=PsaCategory.NONE,
    )
    composite = await ItemComposite.create(
        name="Test Composite",
        lendable=True,
    )
    reservation = await Reservation.create(
        id=uuid4(),
        name="Test Reservation",
        start=date(2026, 1, 1),
        end=date(2026, 1, 3),
        user=uuid4(),
        contact="test@example.com",
        reservation_importance=ReservationImportance.PRIVATE,
    )
    await ReservationItemLink.create(
        item=item,
        reservation=reservation,
        amount=2,
    )
    await ReservationCompositeLink.create(
        composite_item=composite,
        reservation=reservation,
        amount=1,
    )

    reservations = await ReservationService.get_all_reservations()

    assert len(reservations) == 1
    assert reservations[0].id == reservation.id
    assert reservations[0].items == {item.id: 2}
    assert reservations[0].composite_items == {composite.id: 1}


@pytest.mark.asyncio
async def test_get_reservations_by_item_filters_through_item_links(init_db):
    item = await Item.create(
        name="Requested Item",
        lendable=True,
        psa_category=PsaCategory.NONE,
    )
    other_item = await Item.create(
        name="Other Item",
        lendable=True,
        psa_category=PsaCategory.NONE,
    )
    matching_reservation = await Reservation.create(
        id=uuid4(),
        name="Matching Reservation",
        start=date(2026, 1, 1),
        end=date(2026, 1, 3),
        user=uuid4(),
        contact="test@example.com",
        reservation_importance=ReservationImportance.PRIVATE,
    )
    other_reservation = await Reservation.create(
        id=uuid4(),
        name="Other Reservation",
        start=date(2026, 1, 4),
        end=date(2026, 1, 6),
        user=uuid4(),
        contact="test@example.com",
        reservation_importance=ReservationImportance.PRIVATE,
    )
    await ReservationItemLink.create(
        item=item,
        reservation=matching_reservation,
        amount=2,
    )
    await ReservationItemLink.create(
        item=other_item,
        reservation=other_reservation,
        amount=1,
    )

    reservations = await ReservationService.get_reservations_by_item(item.id)

    assert [reservation.id for reservation in reservations] == [matching_reservation.id]
    assert reservations[0].items == {item.id: 2}
    
