# Generated by Django 5.0.1 on 2024-03-26 15:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0104_rename_thumb_img_attraction_thumb_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='pricing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='booking_pricing', to='api.pricing'),
        ),
    ]
