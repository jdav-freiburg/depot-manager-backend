from tortoise import fields
from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [('depot', '0004_item_group')]

    initial = False

    operations = [
        ops.AlterField(
            model_name='Reservation',
            name='start',
            field=fields.DateField(null=False),
        ),
        ops.AlterField(
            model_name='Reservation',
            name='end',
            field=fields.DateField(null=False),
        ),
        ops.AlterField(
            model_name='ItemInstance',
            name='manufacture_date',
            field=fields.DateField(null=False),
        ),
        ops.AlterField(
            model_name='ItemInstance',
            name='purchase_date',
            field=fields.DateField(null=False),
        ),
        ops.AlterField(
            model_name='ItemInstance',
            name='first_use_date',
            field=fields.DateField(null=False),
        ),
        ops.AlterField(
            model_name='ReservationItemLink',
            name='borrowed',
            field=fields.DateField(null=True),
        ),
        ops.AlterField(
            model_name='ReservationItemLink',
            name='returned',
            field=fields.DateField(null=True),
        ),
        ops.AlterField(
            model_name='ReservationCompositeLink',
            name='borrowed',
            field=fields.DateField(null=True),
        ),
        ops.AlterField(
            model_name='ReservationCompositeLink',
            name='returned',
            field=fields.DateField(null=True),
        ),
        ops.AlterField(
            model_name='NewsEntry',
            name='expires',
            field=fields.DateField(null=True),
        ),
    ]
