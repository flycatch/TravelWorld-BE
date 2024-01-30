# Generated by Django 5.0.1 on 2024-01-30 11:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_remove_agent_status_booking_is_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='attraction',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='cancellationpolicy',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='city',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='country',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='currency',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='exclusions',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='guide',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='hoteldetails',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='inclusions',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='informationactivities',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='informations',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='itinerary',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='itineraryday',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='package',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='packagecategory',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='pricing',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='state',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='thingstocarry',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='tourcategory',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='tourtype',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='userreview',
            name='is_active',
        ),
        migrations.AddField(
            model_name='activity',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='attraction',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='booking',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='cancellationpolicy',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='city',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='country',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='currency',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='exclusions',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='guide',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='hoteldetails',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='inclusions',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='informationactivities',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='informations',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='itineraryday',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='package',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='packagecategory',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='pricing',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='state',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='thingstocarry',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='tourcategory',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='tourtype',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AddField(
            model_name='userreview',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='package',
            name='drop_point',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Drop Point'),
        ),
        migrations.AlterField(
            model_name='package',
            name='drop_time',
            field=models.DateTimeField(verbose_name='Drop Time'),
        ),
        migrations.AlterField(
            model_name='package',
            name='duration_day',
            field=models.IntegerField(verbose_name='Duration Day'),
        ),
        migrations.AlterField(
            model_name='package',
            name='pickup_point',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Pickup Point'),
        ),
        migrations.AlterField(
            model_name='package',
            name='pickup_time',
            field=models.DateTimeField(verbose_name='Pickup Time'),
        ),
        migrations.AlterField(
            model_name='package',
            name='tour_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='api.tourtype', verbose_name='Tour Type'),
        ),
    ]
