# Generated by Django 5.1.5 on 2025-02-02 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KidVenture', '0012_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/'),
        ),
    ]
