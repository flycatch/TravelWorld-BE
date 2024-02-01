# Generated by Django 5.0.1 on 2024-01-29 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_alter_activity_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='is_approved',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='is_rejected',
        ),
        migrations.AddField(
            model_name='activity',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
    ]