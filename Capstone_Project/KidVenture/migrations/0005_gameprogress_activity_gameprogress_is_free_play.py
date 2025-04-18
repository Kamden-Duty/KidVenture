# Generated by Django 5.1.5 on 2025-04-03 23:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KidVenture', '0004_alter_gameprogress_level_alter_gameprogress_mistakes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameprogress',
            name='activity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='KidVenture.activity'),
        ),
        migrations.AddField(
            model_name='gameprogress',
            name='is_free_play',
            field=models.BooleanField(default=True),
        ),
    ]
