from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class PsaCategory(StrEnum):
    NONE = 'none'
    CAT_1 = "cat_1"
    CAT_2 = "cat_2"
    CAT_3 = "cat_3"


class ItemGroup(Model):
    class Meta:
        table: str = "depot_item_group"

    id = fields.UUIDField(primary_key=True)

    parent = fields.ForeignKeyField("depot.ItemGroup", null=True, on_delete=fields.RESTRICT,
                                    related_name="child",
                                    description="Used to build up a tree like structure of groups")

    name = fields.data.TextField(null=False)
    description = fields.data.TextField()
    manufacturer = fields.CharField(max_length=255, null=True)
    model = fields.CharField(max_length=255, null=True, description="Model label of this itemgroup")

    id_prefix = fields.CharField(max_length=90, null=True, description="prefix of the external ID")
    id_next = fields.IntField(null=False, default=1, description="The next free numerical suffix that"
                                                                 " can be given to the next item")
    enforce_exact_item = fields.BooleanField(null=False, default=False,
                                             description="true if the user can only lend a specific item and not "
                                                         "any of the group")

    max_lifespan = fields.TimeDeltaField(null=True)
    max_usage_span = fields.TimeDeltaField(null=True)
    psa_category = fields.CharEnumField(PsaCategory)
    data = fields.JSONField(null=True)

    @property
    def is_root(self) -> bool:
        """
        tells if this group is a root node, meaning it has no parents
        """
        return self.parent is None

    @classmethod
    def get_next_external_id(self) -> str:
        return f"[{self.id_prefix}-{self.id_next}]"
