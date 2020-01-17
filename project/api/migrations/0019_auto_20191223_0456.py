# Generated by Django 2.2.9 on 2019-12-23 04:56

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_auto_20190809_0035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalspacetimevolume',
            name='visual_center',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='spacetimevolume',
            name='visual_center',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]