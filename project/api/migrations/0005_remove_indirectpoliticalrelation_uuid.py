# Generated by Django 2.1.2 on 2018-11-19 03:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20181119_0315'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='indirectpoliticalrelation',
            name='uuid',
        ),
    ]
