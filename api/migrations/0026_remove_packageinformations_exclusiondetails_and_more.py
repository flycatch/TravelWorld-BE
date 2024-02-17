# Generated by Django 5.0.1 on 2024-02-17 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0025_remove_cancellationpolicy_category_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='packageinformations',
            name='exclusiondetails',
        ),
        migrations.RemoveField(
            model_name='packageinformations',
            name='inclusiondetails',
        ),
        migrations.AddField(
            model_name='packageinformations',
            name='exclusiondetails',
            field=models.ManyToManyField(blank=True, related_name='packageinformations_exclusionclusion', to='api.itineraryday'),
        ),
        migrations.AddField(
            model_name='packageinformations',
            name='inclusiondetails',
            field=models.ManyToManyField(blank=True, related_name='packageinformations_inclusion', to='api.itineraryday'),
        ),
    ]
