# Generated by Django 5.0.1 on 2024-03-07 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0062_userreviewimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='cancellation_reason',
            field=models.CharField(blank=True, choices=[('ORDERED', 'ORDERED'), ('SUCCESSFUL', 'SUCCESSFUL'), ('CANCELLED', 'CANCELLED'), ('REFUNDED REQUESTED', 'REFUNDED REQUESTED'), ('REFUNDED', 'REFUNDED'), ('FAILED', 'FAILED')], max_length=50, null=True, verbose_name='CANCELLATION REASON'),
        ),
    ]