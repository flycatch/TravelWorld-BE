# Generated by Django 5.0.1 on 2024-03-12 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0072_rename_is_viewed_userreview_is_reviewed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreview',
            name='rating',
            field=models.IntegerField(blank=True, null=True, verbose_name='Rating'),
        ),
    ]