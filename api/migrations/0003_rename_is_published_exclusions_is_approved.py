# Generated by Django 5.0.1 on 2024-01-29 04:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_activity_options_alter_attraction_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exclusions',
            old_name='is_published',
            new_name='is_approved',
        ),
    ]
