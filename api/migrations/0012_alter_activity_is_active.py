# Generated by Django 5.0.1 on 2024-01-29 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_rename_is_published_activity_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]