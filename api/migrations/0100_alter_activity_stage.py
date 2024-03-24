# Generated by Django 5.0.1 on 2024-03-24 06:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0099_remove_activityinclusions_activity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='stage',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('in-progress', 'In-Progress')], default='pending', max_length=20, verbose_name='Stage'),
        ),
    ]