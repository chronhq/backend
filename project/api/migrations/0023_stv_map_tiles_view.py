from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_mvtlayers_tilelayout'),
    ]

    operations = [
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
                , api_territorialentity.color
                , api_territorialentity.admin_level
            FROM api_spacetimevolume
            JOIN api_territorialentity
            ON api_spacetimevolume.entity_id = api_territorialentity.id
            """,
            reverse_sql='DROP VIEW IF EXISTS view_stvmap;'
        )
    ]
