# Generated by Django 2.1.4 on 2019-03-04 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection_module', '0005_auto_20190302_0508'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='external_operation_id',
            field=models.CharField(default=None, max_length=150),
            preserve_default=False,
        ),
    ]