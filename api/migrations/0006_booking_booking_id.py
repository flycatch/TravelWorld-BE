# Generated by Django 5.0.1 on 2024-02-13 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_rename_end_date_booking_check_in_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='booking_id',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]