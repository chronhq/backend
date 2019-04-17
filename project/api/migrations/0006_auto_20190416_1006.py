# Generated by Django 2.1.7 on 2019-04-16 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("api", "0005_auto_20190325_2320")]

    operations = [
        migrations.RemoveField(model_name="cacheddata", name="date"),
        migrations.RemoveField(model_name="city", name="dissolution_date"),
        migrations.RemoveField(model_name="city", name="inception_date"),
        migrations.RemoveField(model_name="historicalcacheddata", name="date"),
        migrations.RemoveField(model_name="historicalcity", name="dissolution_date"),
        migrations.RemoveField(model_name="historicalcity", name="inception_date"),
        migrations.RemoveField(model_name="historicalnarration", name="map_datetime"),
        migrations.RemoveField(
            model_name="historicalpoliticalrelation", name="end_date"
        ),
        migrations.RemoveField(
            model_name="historicalpoliticalrelation", name="start_date"
        ),
        migrations.RemoveField(model_name="historicalspacetimevolume", name="end_date"),
        migrations.RemoveField(
            model_name="historicalspacetimevolume", name="start_date"
        ),
        migrations.RemoveField(model_name="narration", name="map_datetime"),
        migrations.RemoveField(model_name="politicalrelation", name="end_date"),
        migrations.RemoveField(model_name="politicalrelation", name="start_date"),
        migrations.RemoveField(model_name="spacetimevolume", name="end_date"),
        migrations.RemoveField(model_name="spacetimevolume", name="start_date"),
    ]