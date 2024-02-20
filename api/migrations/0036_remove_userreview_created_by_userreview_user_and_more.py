# Generated by Django 5.0.1 on 2024-02-20 08:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_userreview_object_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userreview',
            name='created_by',
        ),
        migrations.AddField(
            model_name='userreview',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_review', to='api.user'),
        ),
        migrations.AlterField(
            model_name='userreview',
            name='package',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='package_review', to='api.package'),
        ),
    ]