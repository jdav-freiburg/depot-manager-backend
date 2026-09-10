

from tortoise import fields
from tortoise.models import Model


class ItemGroup(Model):
    class Meta:
        table: str = "depot_item_group"

    id = fields.UUIDField(primary_key=True)

    parent = fields.ForeignKeyField("depot.ItemGroup", null=True, on_delete=fields.RESTRICT,
                                    related_name="children",
                                    description="Used to build up a tree like structure of groups")

    name = fields.TextField(null=False)
    description = fields.TextField()

    @property
    def is_root(self) -> bool:
        """
        tells if this group is a root node, meaning it has no parents
        """
        return self.parent is None

