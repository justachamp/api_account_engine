# Generated by Django 2.1.4 on 2019-03-01 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection_module', '0002_auto_20190301_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payer',
            name='contact_data',
            field=models.EmailField(max_length=150),
        ),
    ]