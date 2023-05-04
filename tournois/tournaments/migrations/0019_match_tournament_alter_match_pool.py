# Generated by Django 4.2 on 2023-05-03 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0018_merge_0013_match_localisation_0017_match_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='tournament',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tournaments.tournament'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='match',
            name='pool',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='tournaments.pool'),
        ),
    ]
