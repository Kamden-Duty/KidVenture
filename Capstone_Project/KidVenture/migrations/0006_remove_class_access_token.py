# Generated by Django 5.1.5 on 2025-01-22 02:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('KidVenture', '0005_alter_class_access_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='access_token',
        ),
    ]
