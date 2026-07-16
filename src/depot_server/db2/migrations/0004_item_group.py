from orjson import loads
from tortoise import fields
from tortoise import migrations
from tortoise.fields.data import JSON_DUMPS
from tortoise.migrations import operations as ops

from depot_server.db2.models.item.item_group import PsaCategory


class Migration(migrations.Migration):
    dependencies = [('depot', '0003_news')]

    initial = False

    operations = [
        ops.AlterField(
            model_name='ItemGroup',
            name='id_prefix',
            field=fields.CharField(null=True, description='prefix of the external ID', max_length=90),
        ),
        ops.AddField(
            model_name='ItemGroup',
            name='data',
            field=fields.JSONField(null=True, encoder=JSON_DUMPS, decoder=loads),
        ),
        ops.AddField(
            model_name='ItemGroup',
            name='manufacturer',
            field=fields.CharField(null=True, max_length=255),
        ),
        ops.AddField(
            model_name='ItemGroup',
            name='max_lifespan',
            field=fields.TimeDeltaField(null=True),
        ),
        ops.AddField(
            model_name='ItemGroup',
            name='max_usage_span',
            field=fields.TimeDeltaField(null=True),
        ),
        ops.AddField(
            model_name='ItemGroup',
            name='model',
            field=fields.CharField(null=True, description='Model label of this itemgroup', max_length=255),
        ),
        ops.AddField(
            model_name='ItemGroup',
            name='psa_category',
            field=fields.CharEnumField(description='NONE: none\nCAT_1: cat_1\nCAT_2: cat_2\nCAT_3: cat_3',
                                       enum_type=PsaCategory, max_length=5),
        ),
    ]
