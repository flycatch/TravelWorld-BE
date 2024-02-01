# Generated by Django 5.0.1 on 2024-01-31 05:18

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_alter_agent_managers_alter_baseuser_managers_and_more'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='agent',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='baseuser',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]