# Generated by Django 5.0.1 on 2024-02-22 18:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0042_remove_city_image_remove_state_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreview',
            name='agent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_review_agent', to='api.agent'),
        ),
        migrations.AddField(
            model_name='userreview',
            name='booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_review_booking', to='api.booking'),
        ),
    ]
