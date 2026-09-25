from datetime import date
from uuid import uuid4

import pytest
import pytest_asyncio
from tortoise import Tortoise

from depot_server.db2.models import Reservation, LinkReservationLendable, Lendable
from depot_server.db2.models.item.item import PsaCategory
from depot_server.db2.models.common import ReservationImportance
from depot_server.db2.repository.item.repo_reservation import ReservationRepo, ReservationRepoLinkLendable


@pytest_asyncio.fixture
async def init_db():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"depot": ["depot_server.db2.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()

@pytest.mark.asyncio
async def test_get_all_with_links(init_db):
    lendable1 = await Lendable.create(
        name="Lendable 1",
        psa_category=PsaCategory.NONE,
    )
    lendable2 = await Lendable.create(
        name="Lendable 2",
        psa_category=PsaCategory.NONE,
    )
    reservation = await Reservation.create(
        name="Test Reservation",
        start=date(2026, 1, 1),
        end=date(2026, 1, 3),
        user=uuid4(),
        contact="test@example.com",
        reservation_importance=ReservationImportance.PRIVATE,
    )
    reservation2 = await Reservation.create(
        name="Test Reservation 2",
        start=date(2026, 1, 4),
        end=date(2026, 1, 6),
        user=uuid4(),
        contact="test@example.com",
        reservation_importance=ReservationImportance.TEAM,
    )

    link1 = await LinkReservationLendable.create(
        lendable=lendable1,
        reservation=reservation,
        amount=2,
    )
    link2 =await LinkReservationLendable.create(
        lendable=lendable2,
        reservation=reservation,
        amount=1,
    )
    link3 = await LinkReservationLendable.create(
        lendable=lendable1,
        reservation=reservation2,
        amount=3,
    )

    reservations = await ReservationRepo.get_all_with_links()

    assert len(reservations) == 2
    assert reservations[0].id == reservation.id
    assert reservations[1].id == reservation2.id
    assert reservations[0].reservation_lendable_links[0].id == link1.id
    assert reservations[0].reservation_lendable_links[1].id == link2.id
    assert reservations[1].reservation_lendable_links[0].id == link3.id
    
@pytest.mark.asyncio
async def test_get_lendable_links_in_timespan(init_db):
    lendable = await Lendable.create(
        name="Test Item",
        psa_category=PsaCategory.NONE,
    )
    other_lendable = await Lendable.create(
        name="Other Item",
        psa_category=PsaCategory.NONE,
    )
    other_reservation = await Reservation.create(
        name="Other Reservation",
        start=date(2026, 1, 1),
        end=date(2026, 1, 30),
        user=uuid4(),
        contact="test@example.com",
        reservation_importance=ReservationImportance.PRIVATE,
    )
    other_link = await LinkReservationLendable.create(
        lendable=other_lendable,
        reservation=other_reservation,
        amount=1,
    )

    reservation1 = await Reservation.create(
        name="Reservation 1",
        start=date(2026, 1, 1),
        end=date(2026, 1, 3),
        user=uuid4(),
        contact="test@example.com",
        reservation_importance=ReservationImportance.PRIVATE,
    )
    reservation2 = await Reservation.create(
        name="Reservation 2",
        start=date(2026, 1, 4),
        end=date(2026, 1, 6),
        user=uuid4(),
        contact="test@example.com",
        reservation_importance=ReservationImportance.PRIVATE,
    )
    link1 = await LinkReservationLendable.create(
        lendable=lendable,
        reservation=reservation1,
        amount=2,
    )
    link2 = await LinkReservationLendable.create(
        lendable=lendable,
        reservation=reservation2,
        amount=3,
    )

    links = await ReservationRepoLinkLendable.get_lendable_links_in_timespan(
        lendable.id,
        date(2026, 1, 1),
        date(2026, 1, 3)
    )
    assert len(links) == 1
    assert links[0].id == link1.id

    links = await ReservationRepoLinkLendable.get_lendable_links_in_timespan(
        lendable.id,
        date(2026, 1, 4),
        date(2026, 1, 6)
    )
    assert len(links) == 1
    assert links[0].id == link2.id

    links = await ReservationRepoLinkLendable.get_lendable_links_in_timespan(
        lendable.id,
        date(2026, 1, 1),
        date(2026, 1, 6)
    )
    assert len(links) == 2