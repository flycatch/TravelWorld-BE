# Generated by Django 5.0.1 on 2024-03-23 06:00

import django_ckeditor_5.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0097_remove_itinerary_itinerary_day_itinerary_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityitinerary',
            name='itinerary_day',
        ),
        migrations.AddField(
            model_name='activityitinerary',
            name='description',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='activityitinerary',
            name='overview',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True, verbose_name='Overview'),
        ),
        migrations.DeleteModel(
            name='ActivityItineraryDay',
        ),
    ]