# Generated by Django 4.2 on 2023-05-04 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0019_alter_match_pool'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='pool',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tournaments.pool'),
        ),
    ]