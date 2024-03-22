# Generated by Django 5.0.1 on 2024-03-21 14:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0090_alter_pricing_activity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityimage',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_image', to='api.activity'),
        ),
    ]