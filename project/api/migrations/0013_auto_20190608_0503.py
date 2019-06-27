# Generated by Django 2.2.1 on 2019-06-08 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20190511_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalterritorialentity',
            name='stv_count',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='territorialentity',
            name='predecessor',
            field=models.ManyToManyField(blank=True, to='api.TerritorialEntity'),
        ),
        migrations.AddField(
            model_name='territorialentity',
            name='stv_count',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='historicalterritorialentity',
            name='dissolution_date',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='territorialentity',
            name='dissolution_date',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
    ]