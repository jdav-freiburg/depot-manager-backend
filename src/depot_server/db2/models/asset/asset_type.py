from typing import Self

from tortoise import fields
from tortoise.models import Model


class AssetType(Model):
    """
    Asset Type Model:
    represents the kind and intended use of an asset.
    This is not an enum, since the possible types should be alterable by
    the user during the use of the application.
    This will get seeded initially
    """
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    description = fields.TextField()

    @classmethod
    def get_seed_data(cls) -> list[Self]:
        return [
            AssetType.construct(name="item_image", description="Images showing the item on the website"),
            AssetType.construct(name="gal", description="Gebrauchsanleitung"),
            AssetType.construct(name="datasheet", description="Datasheet for a specific item, "
                                                              "usually lists item specific properties"),
            AssetType.construct(name="inspection_instruction", description="Instructions on how to check the item's"
                                                                           "safety and functionality properly"),
            AssetType.construct(name="map", description="Asset helping the user finding an item"),
            AssetType.construct(name="service_certificate", description="Certificate from external service contractor"
                                                                        "certifying safety of the device"),
        ]
