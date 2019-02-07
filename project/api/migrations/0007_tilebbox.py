from django.db import migrations


def get_sql(filename):
    with open('api/sql/' + filename) as f:
        return f.read()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_merge_20190114_0002'),
    ]

    operations = [
        migrations.RunSQL(
            get_sql('TileBBox.sql'),
            reverse_sql='drop function if exists TileBBox(z int, x int, y int, srid int) restrict;',
            elidable=False
        )
    ]
