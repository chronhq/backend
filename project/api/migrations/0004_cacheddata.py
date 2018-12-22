# Generated by Django 2.1.2 on 2018-12-22 20:11

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20181217_0458'),
    ]

    operations = [
        migrations.CreateModel(
            name='CachedData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wikidata_id', models.PositiveIntegerField(unique=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('date', models.DateField()),
                ('rank', models.PositiveIntegerField()),
                ('event_type', models.PositiveIntegerField(choices=[(178561, 'battle'), (131569, 'treaty')])),
            ],
        ),
    ]
