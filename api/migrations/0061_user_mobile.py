# Generated by Django 5.0.1 on 2024-03-05 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0060_agent_agent_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='mobile',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
    ]
