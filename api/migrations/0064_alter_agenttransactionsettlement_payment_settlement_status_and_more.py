# Generated by Django 5.0.1 on 2024-03-07 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0063_booking_cancellation_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agenttransactionsettlement',
            name='payment_settlement_status',
            field=models.CharField(blank=True, choices=[('PENDING', 'PENDING'), ('SUCCESSFUL', 'SUCCESSFUL'), ('REJECTED', 'REJECTED')], default='PENDING', max_length=50, null=True, verbose_name='Payment Settlement Status'),
        ),
        migrations.AlterField(
            model_name='userrefundtransaction',
            name='refund_amount',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True, verbose_name='Refund Amount'),
        ),
        migrations.AlterField(
            model_name='userrefundtransaction',
            name='refund_status',
            field=models.CharField(blank=True, choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('REFUNDED', 'REFUNDED')], max_length=50, null=True, verbose_name='Refund Status'),
        ),
    ]
