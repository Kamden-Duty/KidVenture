# Generated by Django 5.1.3 on 2025-01-22 17:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KidVenture', '0007_class_access_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('progress', models.IntegerField(default=0)),
                ('url_name', models.CharField(blank=True, max_length=50, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='KidVenture.student')),
            ],
        ),
    ]
