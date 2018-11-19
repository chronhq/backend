from django.db import migrations

def get_sql(filename):
    with open('api/sql/' + filename) as f:
        return f.read()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20181119_1930'),
    ]

    operations = [
        # Create some indexes
        migrations.RunSQL(get_sql('index.sql')),
        # Add a constraint for recursivity
        migrations.RunSQL(get_sql('constraint.sql')),
        # Add a PostgreSQL trigger to manage the path automatically
        migrations.RunSQL(get_sql('triggers.sql')),
    ]