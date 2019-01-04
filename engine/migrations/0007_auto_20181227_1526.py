# Generated by Django 2.1.4 on 2018-12-27 15:26

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0006_auto_20181227_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='total_amount',
            field=models.DecimalField(decimal_places=5, default=Decimal('0.00000'), max_digits=20),
        ),
    ]
