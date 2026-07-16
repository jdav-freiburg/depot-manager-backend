from uuid import uuid4

from orjson import loads
from tortoise import fields
from tortoise import migrations
from tortoise.fields.data import JSON_DUMPS
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [('depot', '0001_initial')]

    initial = False

    operations = [
        ops.CreateModel(
            name='Changelog',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('type_', fields.CharField(description='The type of the object that was changed', max_length=100)),
                ('type_id', fields.UUIDField(description='The identifier of the object that was changed')),
                ('timestamp', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('user_id', fields.CharField(max_length=100)),
                ('comment',
                 fields.TextField(description="'Commit' message describing why the change was made", unique=False)),
                ('old', fields.JSONField(description='The state of the object before the change', encoder=JSON_DUMPS,
                                         decoder=loads)),
                ('new', fields.JSONField(description='The state of the object after the change', encoder=JSON_DUMPS,
                                         decoder=loads)),
            ],
            options={'table': 'depot_changelog', 'app': 'depot', 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]
