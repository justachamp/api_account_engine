# Generated by Django 2.1.4 on 2019-03-04 21:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing_module', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='billingcontact',
            old_name='rut',
            new_name='document_number',
        ),
    ]
