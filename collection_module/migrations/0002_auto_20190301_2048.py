# Generated by Django 2.1.4 on 2019-03-01 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection_module', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guaranteedocument',
            name='fines',
        ),
        migrations.AlterField(
            model_name='guaranteedocument',
            name='document_description',
            field=models.CharField(max_length=350),
        ),
    ]
