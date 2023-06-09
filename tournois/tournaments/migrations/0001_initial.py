# Generated by Django 4.2 on 2023-04-17 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tournoi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('place', models.CharField(max_length=200, null=True)),
                ('date', models.CharField(max_length=200, null=True)),
                ('N_pools', models.IntegerField(verbose_name='Number of pools')),
                ('N_teams_per_pools', models.IntegerField(verbose_name='Number of teams per pools')),
            ],
        ),
    ]
