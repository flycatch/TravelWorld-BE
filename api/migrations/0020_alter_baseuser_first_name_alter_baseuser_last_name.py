# Generated by Django 5.0.1 on 2024-01-30 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_remove_exclusions_is_approved_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Last Name'),
        ),
    ]