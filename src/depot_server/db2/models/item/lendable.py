from tortoise import fields
from tortoise.models import Model
from tortoise.validators import MinValueValidator
from tortoise.migrations.constraints import CheckConstraint


class Lendable(Model):
    class Meta:
        table: str = "depot_lendable"
        constraints = [
            CheckConstraint("in_limbus >= 0", name="check_in_limbus_non_negative")
        ]
    id = fields.UUIDField(primary_key=True)
    name = fields.TextField(null=False)
    description = fields.TextField(null=True)
    in_limbus = fields.IntField(null=False, default=0, validators=[MinValueValidator(0)],
                                description="The amount of this items where it is unsure if they are lost or if they return.")
    lendable_group = fields.ForeignKeyField("depot.LendableGroup", null=True, on_delete=fields.RESTRICT,
                                     related_name="lendable",
                                     description="The group this lendable belongs to. This is used to build a tree like structure.")
    storage_location = fields.ForeignKeyField("depot.StorageLocation", on_delete=fields.RESTRICT, null=True,
                                              related_name="lendable")
    ausgabepflichtig = fields.BooleanField(default=False, null=False, description="Must be handed out by a member of the depot team.")
    assets = fields.ManyToManyField("depot.Asset", on_delete=fields.RESTRICT, related_name="lendable")
    changed_at = fields.DatetimeField(auto_now_add=True)
    lendable_purpose_link: fields.ReverseRelation["LinkLendablePurpose"]

    @property
    async def is_lendable(self) -> bool:
        """
        Checks if the item is lendable. An item is considered lendable if it has at least one link to a purpose.
        """
        return await self.lendable_purpose_link.all().exists()


class LinkLendablePurpose(Model):
    class Meta:
        table: str = "depot_link_lendable__purpose"
        unique_together = (("purpose",),)

    id = fields.UUIDField(primary_key=True)

    lendable = fields.ForeignKeyField("depot.Lendable", null=False, related_name="lendable_purpose_link")
    purpose = fields.ForeignKeyField("depot.ItemPurpose", null=False, related_name="lendable_purpose_link", unique=True)
    amount = fields.IntField(null=False, validators=[MinValueValidator(1)], description="The quantity of the item in the lendable group")
    created_at = fields.DatetimeField(auto_now_add=True)


class LinkLendablePurposeArchive(Model):
    class Meta:
        table: str = "depot_link_lendable__purpose_archive"

    id = fields.UUIDField(primary_key=True)

    lendable = fields.ForeignKeyField("depot.Lendable", null=False, related_name="lendable_purpose_link_archive")
    purpose = fields.ForeignKeyField("depot.ItemPurpose", null=False, related_name="lendable_purpose_link_archive")
    amount = fields.IntField(null=False, validators=[MinValueValidator(1)], description="The quantity of the item in the lendable group")
    created_at = fields.DatetimeField(null=False, description="The date when the link was created in the LinkLendablePurpose table.")
    change_date = fields.DatetimeField(auto_now_add=True, description="The date when the link was archived. This is the date when the link stopped being active in the LinkLendablePurpose table and was moved to the archive table.")