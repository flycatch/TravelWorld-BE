# Generated by Django 5.0.1 on 2024-01-29 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_alter_agent_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='baseuser',
            options={'verbose_name': 'Base User', 'verbose_name_plural': 'Base Users'},
        ),
        migrations.RemoveField(
            model_name='package',
            name='is_approved',
        ),
        migrations.RemoveField(
            model_name='package',
            name='is_published',
        ),
        migrations.RemoveField(
            model_name='package',
            name='is_rejected',
        ),
        migrations.AddField(
            model_name='package',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='package',
            name='stage',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='agent',
            name='stage',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Stage'),
        ),
    ]
