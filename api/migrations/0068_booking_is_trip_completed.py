# Generated by Django 5.0.1 on 2024-03-08 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0067_alter_booking_cancellation_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='is_trip_completed',
            field=models.BooleanField(default=0),
        ),
    ]
