# Generated by Django 5.1.5 on 2025-01-22 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KidVenture', '0002_rename_student_user_is_student_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='class',
            name='access_token',
            field=models.CharField(default=None, editable=False, max_length=4, unique=True),
        ),
    ]
