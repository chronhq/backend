# Generated by Django 2.2.4 on 2019-08-08 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_historicalsymbol_symbol_symbolfeature'),
    ]

    operations = [
        migrations.AddField(
            model_name='symbol',
            name='narration',
            field=models.ManyToManyField(related_name='symbols', to='api.Narration'),
        ),
    ]