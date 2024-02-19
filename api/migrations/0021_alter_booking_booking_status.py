# Generated by Django 5.0.1 on 2024-02-16 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_remove_itinerary_important_message_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='booking_status',
            field=models.CharField(blank=True, choices=[('ORDERED', 'ORDERED'), ('SUCCESSFUL', 'SUCCESSFUL'), ('CANCELLED', 'CANCELLED'), ('REFUNDED REQUESTED', 'REFUNDED REQUESTED'), ('REFUNDED', 'REFUNDED'), ('FAILED', 'FAILED')], max_length=50, null=True),
        ),
    ]