# Generated by Django 5.0.1 on 2024-02-29 04:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0050_alter_activityexclusioninformation_exclusion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attraction',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attraction_state', to='api.city'),
        ),
        migrations.AddField(
            model_name='attraction',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attaction_state', to='api.state'),
        ),
    ]
