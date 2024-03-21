# Generated by Django 5.0.1 on 2024-03-20 19:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0085_alter_booking_booking_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='city',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='country',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='state',
        ),
        migrations.RemoveField(
            model_name='package',
            name='city',
        ),
        migrations.RemoveField(
            model_name='package',
            name='country',
        ),
        migrations.RemoveField(
            model_name='package',
            name='state',
        ),
        migrations.RemoveField(
            model_name='packageinformations',
            name='important_message',
        ),
        migrations.AddField(
            model_name='itinerary',
            name='important_message',
            field=models.TextField(blank=True, default='', verbose_name='important Message'),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='things_to_carry',
            field=models.TextField(blank=True, default='', verbose_name='Things to carry'),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location_country', to='api.country')),
                ('destinations', models.ManyToManyField(blank=True, related_name='location_destinations', to='api.city')),
                ('state', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location_state', to='api.state')),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='locations',
            field=models.ManyToManyField(blank=True, related_name='activity_location', to='api.location'),
        ),
        migrations.AddField(
            model_name='package',
            name='locations',
            field=models.ManyToManyField(blank=True, related_name='package_location', to='api.location'),
        ),
    ]