from uuid import uuid4

from tortoise import fields
from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [('depot', '0002_changelog')]

    initial = False

    operations = [
        ops.CreateModel(
            name='NewsEntry',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('title', fields.CharField(max_length=255)),
                ('timestamp', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('author', fields.CharField(max_length=255)),
                ('text', fields.TextField(null=True, unique=False)),
                ('expires', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('is_visible', fields.BooleanField(default=True)),
                ('is_pinned', fields.BooleanField(default=False)),
            ],
            options={'table': 'depot_news_entry', 'app': 'depot', 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]
