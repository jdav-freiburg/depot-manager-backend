from tortoise import fields
from tortoise.models import Model


class ItemGroup(Model):
    id = fields.UUIDField(pk=True)
    name = fields.data.TextField(null=False)
    description = fields.data.TextField()
    parent = fields.ForeignKeyField(
        "item.Itemgroup",
            null=True,
            on_delete=fields.RESTRICT,
            description="Used to build up a tree like structure of groups")
    id_prefix = fields.CharField(
            max_length=90,
            null=False,
            description="prefix of the external ID"
            )
    id_next = fields.IntField(
            null=False,
          default=1,
          description="The next free numerical suffix that can be given to the next item")
    enforce_exact_item = fields.BooleanField(
            null=False,
            default=False,
            description="true if the user can only lend a specific item and not any of the group")

    @property
    def is_root(self) -> bool:
        """
        tells if this group is a root node, meaning it has no parents
        """
        return self.parent is None

    @classmethod
    def get_next_external_id(self) -> str:
        return f"[{self.id_prefix}-{self.id_next}"
