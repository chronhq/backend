# Generated by Django 2.1.4 on 2018-12-30 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_cacheddata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cacheddata',
            name='wikidata_id',
            field=models.PositiveIntegerField(),
        ),
    ]
