# Generated by Django 2.1.4 on 2019-02-28 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0012_auto_20190227_1809'),
    ]

    operations = [
        migrations.RenameField(
            model_name='posting',
            old_name='assetType',
            new_name='asset_type',
        ),
    ]
