from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_api_ltree'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='directpoliticalrelation',
            options={},
        ),
        migrations.AlterModelOptions(
            name='indirectpoliticalrelation',
            options={},
        ),
        migrations.AddField(
            model_name='directpoliticalrelation',
            name='child_entity',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='directpoliticalrelation_parents', to='api.PoliticalEntity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='directpoliticalrelation',
            name='parent_entity',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='directpoliticalrelation_children', to='api.PoliticalEntity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='indirectpoliticalrelation',
            name='child_entity',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='indirectpoliticalrelation_parents', to='api.PoliticalEntity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='indirectpoliticalrelation',
            name='parent_entity',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='indirectpoliticalrelation_children', to='api.PoliticalEntity'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='directpoliticalrelation',
            name='uuid',
        ),
        migrations.AlterUniqueTogether(
            name='directpoliticalrelation',
            unique_together={('parent_entity', 'child_entity')},
        ),
        migrations.AlterUniqueTogether(
            name='indirectpoliticalrelation',
            unique_together={('parent_entity', 'child_entity')},
        ),
    ]
