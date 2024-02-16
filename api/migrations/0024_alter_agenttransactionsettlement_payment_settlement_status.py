# Generated by Django 5.0.1 on 2024-02-16 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_alter_contactperson_booking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agenttransactionsettlement',
            name='payment_settlement_status',
            field=models.CharField(blank=True, choices=[('PENDING', 'PENDING'), ('SUCCESSFUL', 'SUCCESSFUL'), ('FAILED', 'FAILED')], default='PENDING', max_length=50, null=True),
        ),
    ]
