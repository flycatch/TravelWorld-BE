# Generated by Django 5.0.1 on 2024-03-21 05:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0086_remove_activity_city_remove_activity_country_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exclusions',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='inclusions',
            name='icon',
        ),
    ]
