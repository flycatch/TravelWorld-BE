# Generated by Django 5.0.1 on 2024-03-20 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0081_activity_is_popular_baseuser_created_on_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='exclusions',
            name='icon',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='exclusions/'),
        ),
        migrations.AddField(
            model_name='inclusions',
            name='icon',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='inclusions/'),
        ),
    ]
