# Generated by Django 5.0.1 on 2024-02-21 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_tourtype_advanceamountpercentagesetting_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='agenttransactionsettlement',
            name='booking_type',
            field=models.CharField(blank=True, choices=[('PARTIAL PAYMENT', 'PARTIAL PAYMENT'), ('FULL AMOUNT PAYMENT', 'FULL AMOUNT PAYMENT')], max_length=50, null=True),
        ),
    ]
