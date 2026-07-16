from depot_server.api2.models.item_group import ItemGroup
from depot_server.db2.models.item.item_group import ItemGroup as DbItemGroup


def item_group_from_orm(item_group: DbItemGroup) -> ItemGroup:
    return ItemGroup(
        id=item_group.id,
        name=item_group.name,
        description=item_group.description,
        manufacturer=item_group.manufacturer,
        model=item_group.model,
        enforce_exact_item=item_group.enforce_exact_item,
        id_prefix=item_group.id_prefix,
        max_lifespan=item_group.max_lifespan,
        max_usage_span=item_group.max_usage_span,
        psa_category=item_group.psa_category,
        data=item_group.data,
        parent=item_group.parent_id,
    )
