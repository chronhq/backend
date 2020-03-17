import colorfield.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_mvtlayers_tilelayout'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapColorScheme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', colorfield.fields.ColorField(default='#F7F7F7', max_length=18, unique=True)),
                ('pallete', models.TextField(blank=True, max_length=64, null=True)),
                ('main', models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='historicalterritorialentity',
            name='color',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='api.MapColorScheme'),
        ),
        migrations.AlterField(
            model_name='territorialentity',
            name='color',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.MapColorScheme'),
        ),
        migrations.RunSQL(
            """
            CREATE VIEW view_stvmap AS
            SELECT
                api_spacetimevolume.id
                , api_spacetimevolume.start_date::INTEGER
                , api_spacetimevolume.end_date::INTEGER
                , api_spacetimevolume.references
                , api_spacetimevolume.territory
                , api_spacetimevolume.entity_id
                , api_territorialentity.wikidata_id
                , api_mapcolorscheme.color
                , api_territorialentity.admin_level
            FROM api_spacetimevolume
            JOIN api_territorialentity ON api_spacetimevolume.entity_id = api_territorialentity.id
            JOIN api_mapcolorscheme ON api_territorialentity.color = api_mapcolorscheme.id
            """,
            reverse_sql='DROP VIEW IF EXISTS view_stvmap;'
        )
    ]
