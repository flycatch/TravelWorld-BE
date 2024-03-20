# Generated by Django 5.0.1 on 2024-03-13 15:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0076_alter_pricing_blackout_dates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreview',
            name='booking',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_review_booking', to='api.booking'),
        ),
    ]