# Generated by Django 5.0.1 on 2024-02-16 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_alter_agenttransactionsettlement_payment_settlement_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cancellationpolicy',
            name='category',
        ),
        migrations.AddField(
            model_name='cancellationpolicy',
            name='from_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cancellationpolicy',
            name='to_day',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='itinerary',
            name='exclusions',
            field=models.ManyToManyField(blank=True, related_name='itineraries', to='api.exclusions'),
        ),
        migrations.AlterField(
            model_name='itinerary',
            name='inclusions',
            field=models.ManyToManyField(blank=True, related_name='itineraries', to='api.inclusions'),
        ),
    ]