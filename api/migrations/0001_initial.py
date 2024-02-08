# Generated by Django 5.0.1 on 2024-02-08 07:21

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='Last Name')),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Base User',
                'verbose_name_plural': 'Base Users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, default='')),
                ('stage', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Stage')),
            ],
            options={
                'verbose_name': 'Activity',
                'verbose_name_plural': 'Activities',
            },
        ),
        migrations.CreateModel(
            name='Attraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('overview', models.TextField(blank=True, default='')),
            ],
            options={
                'verbose_name': 'Attraction',
                'verbose_name_plural': 'Attractions',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to='city_images/')),
            ],
            options={
                'verbose_name': 'City',
                'verbose_name_plural': 'Cities',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to='country_images/')),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Currency',
                'verbose_name_plural': 'Currency',
            },
        ),
        migrations.CreateModel(
            name='Exclusions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('stage', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Stage')),
            ],
            options={
                'verbose_name': 'Exclusions',
                'verbose_name_plural': 'Exclusions',
            },
        ),
        migrations.CreateModel(
            name='FAQQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('question', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'FAQQuestion',
                'verbose_name_plural': 'FAQQuestions',
            },
        ),
        migrations.CreateModel(
            name='Inclusions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('stage', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Stage')),
            ],
            options={
                'verbose_name': 'Inclusions',
                'verbose_name_plural': 'Inclusions',
            },
        ),
        migrations.CreateModel(
            name='ItineraryDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('day', models.CharField(default='', max_length=255)),
                ('place', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
            ],
            options={
                'verbose_name': 'Itinerary Day',
                'verbose_name_plural': 'Itinerary Day',
            },
        ),
        migrations.CreateModel(
            name='PackageCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Package Category',
                'verbose_name_plural': 'Package Category',
            },
        ),
        migrations.CreateModel(
            name='TourType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Tour Type',
                'verbose_name_plural': 'Tour Type',
            },
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('baseuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('agent_uid', models.CharField(editable=False, max_length=10, unique=True)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_images/agent/')),
                ('stage', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Stage')),
            ],
            options={
                'verbose_name': 'Agent',
                'verbose_name_plural': 'Agents',
            },
            bases=('api.baseuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('baseuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('profile_image', models.ImageField(blank=True, null=True, upload_to='profile_images/user/')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            bases=('api.baseuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ActivityImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to='attraction_images/')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activityimages', to='api.activity')),
            ],
        ),
        migrations.CreateModel(
            name='AttractionImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to='attraction_images/')),
                ('attraction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attracionimages', to='api.attraction')),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='city',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='api.city'),
        ),
        migrations.AddField(
            model_name='activity',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='api.country'),
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('title', models.CharField(max_length=255)),
                ('min_members', models.IntegerField()),
                ('max_members', models.IntegerField()),
                ('duration_day', models.IntegerField(verbose_name='Duration Day')),
                ('duration_hour', models.IntegerField()),
                ('pickup_point', models.CharField(blank=True, max_length=255, null=True, verbose_name='Pickup Point')),
                ('pickup_time', models.DateTimeField(verbose_name='Pickup Time')),
                ('drop_point', models.CharField(blank=True, max_length=255, null=True, verbose_name='Drop Point')),
                ('drop_time', models.DateTimeField(verbose_name='Drop Time')),
                ('stage', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=20, verbose_name='Stage')),
                ('is_submitted', models.BooleanField(default=False)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='api.city')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='api.country')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='api.packagecategory')),
            ],
            options={
                'verbose_name': 'Package',
                'verbose_name_plural': 'Packages',
            },
        ),
        migrations.CreateModel(
            name='Itinerary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('overview', models.TextField(blank=True, default='')),
                ('important_message', models.TextField(blank=True, default='', verbose_name='important Message')),
                ('exclusions', models.ManyToManyField(related_name='itineraries', to='api.exclusions')),
                ('inclusions', models.ManyToManyField(related_name='itineraries', to='api.inclusions')),
                ('itinerary_day', models.ManyToManyField(related_name='itineraries', to='api.itineraryday')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itineraries', to='api.package')),
            ],
            options={
                'verbose_name': 'Itinerary',
                'verbose_name_plural': 'Itinerary',
            },
        ),
        migrations.CreateModel(
            name='Informations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('details', models.TextField(blank=True, default='')),
                ('itinerary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='informations', to='api.itinerary')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='informations', to='api.package')),
            ],
            options={
                'verbose_name': 'Information',
                'verbose_name_plural': 'Informations',
            },
        ),
        migrations.CreateModel(
            name='FAQAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('answer', models.TextField()),
                ('question', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='faqanswer', to='api.faqquestion')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faqanswer', to='api.package')),
            ],
            options={
                'verbose_name': 'FAQAnswer',
                'verbose_name_plural': 'FAQAnswers',
            },
        ),
        migrations.CreateModel(
            name='CancellationPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('category', models.CharField(max_length=255)),
                ('amount_percent', models.CharField(max_length=255)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cancellation_policies', to='api.package')),
            ],
            options={
                'verbose_name': 'Cancellation Policy',
                'verbose_name_plural': 'Cancellation Policies',
            },
        ),
        migrations.CreateModel(
            name='PackageImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to='package_images/')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packageimages', to='api.package')),
            ],
            options={
                'ordering': ('-created_on',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('group_rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('group_commission', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('group_agent_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('pricing_group', models.CharField(choices=[('per_person', 'Per Person'), ('per_group', 'Per Group')], default='per_person', max_length=25)),
                ('adults_rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('adults_commission', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('adults_agent_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('child_rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('child_commission', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('child_agent_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('infant_rate', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('infant_commission', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('infant_agent_amount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pricings', to='api.package')),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pricings', to='api.currency')),
            ],
            options={
                'verbose_name': 'Pricing',
                'verbose_name_plural': 'Pricing',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('name', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to='state_images/')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='states', to='api.country')),
            ],
            options={
                'verbose_name': 'State',
                'verbose_name_plural': 'States',
            },
        ),
        migrations.AddField(
            model_name='package',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='api.state'),
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='api.state'),
        ),
        migrations.AddField(
            model_name='activity',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='api.state'),
        ),
        migrations.CreateModel(
            name='TourCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('type', models.CharField(choices=[('through_out_year', 'Through Out Year'), ('seasonal', 'Seasonal'), ('fixed_departure', 'Fixed Departure')], default='through_out_year', max_length=255)),
                ('start_at', models.DateField(blank=True, null=True)),
                ('end_at', models.DateField(blank=True, null=True)),
                ('selected_week_days', models.CharField(blank=True, max_length=255, null=True)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tour_categories', to='api.package')),
            ],
            options={
                'verbose_name': 'Tour Category',
                'verbose_name_plural': 'Tour Categories',
            },
        ),
        migrations.AddField(
            model_name='package',
            name='tour_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='api.tourtype', verbose_name='Tour Type'),
        ),
        migrations.AddField(
            model_name='package',
            name='agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to='api.agent'),
        ),
        migrations.AddField(
            model_name='activity',
            name='agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='api.agent'),
        ),
        migrations.CreateModel(
            name='UserReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('rating', models.IntegerField()),
                ('review', models.TextField(blank=True, default='')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='api.package')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='api.user')),
            ],
            options={
                'verbose_name': 'User Review',
                'verbose_name_plural': 'User Reviews',
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length=20, verbose_name='Status')),
                ('adult', models.IntegerField()),
                ('child', models.IntegerField()),
                ('infant', models.IntegerField()),
                ('is_cancelled', models.BooleanField(default=False)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='api.package')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='api.user')),
            ],
            options={
                'verbose_name': 'Booking',
                'verbose_name_plural': 'Bookings',
            },
        ),
    ]
