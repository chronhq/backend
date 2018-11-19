import api.ltree
from django.db import migrations, models
from django.contrib.postgres.operations import CreateExtension
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20181119_0215'),
    ]

    operations = [
        # Add the 'ltree' extension to PostgreSQL. Only needed once.
        CreateExtension('ltree'),
        migrations.AddField(
            model_name='directpoliticalrelation',
            name='path',
            field=api.ltree.LtreeField(default=None, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='indirectpoliticalrelation',
            name='path',
            field=api.ltree.LtreeField(default=None, editable=False, null=True),
        ),
    ]
