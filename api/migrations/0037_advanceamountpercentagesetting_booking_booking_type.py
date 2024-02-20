# Generated by Django 5.0.1 on 2024-02-20 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0036_remove_userreview_created_by_userreview_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvanceAmountPercentageSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('percentage', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
            ],
            options={
                'verbose_name': 'Advance Amount Percentage Setting',
                'verbose_name_plural': 'Advance Amount Percentage Settings',
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='booking_type',
            field=models.CharField(blank=True, choices=[('PARTIAL PAYMENT', 'PARTIAL PAYMENT'), ('FULL AMOUNT PAYMENT', 'FULL AMOUNT PAYMENT')], max_length=50, null=True),
        ),
    ]
