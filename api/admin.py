import calendar
from datetime import datetime
from datetime import date

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.admin import AdminSite
from django.contrib.admin.sites import site
from django.template.defaultfilters import truncatechars
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string

from rest_framework.authtoken.models import TokenProxy

from api.common.custom_admin import *
from api.models import *
from api.tasks import *
from api.utils.admin import (stage_colour, status_colour, booking_status_colour,
                             refund_status_colour, account_verification_status_colour)

class AgentAdmin(CustomModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('agent_uid', 
         'agent_name', 'phone', 'email', 'company_id', 'company_name', 
         'company_site', 'message', 'profile_image')}),
        ('Permissions', {'fields': ('stage', 'account_verification_status')}),
        # ('Activity History', {'fields': ('date_joined', 'last_login')}),
    )

    list_display = ("agent_uid", "company_name", "agent_name", "email", "phone",
                    "stage_colour", "account_verification_status_colour")
    list_filter = ("stage", "account_verification_status")
    search_fields = ("agent_uid", "company_name", "agent_name", "email", "phone")
    readonly_fields = ("agent_uid", "company_id", "company_name", "company_site",
                       "message", "agent_name", "email", "phone", "profile_image")

    inlines = [AgentBankDetailsInline]

    def stage_colour(self, obj):
        return stage_colour(obj.stage)

    def account_verification_status_colour(self, obj):
        return stage_colour(obj.account_verification_status)

    def status_colour(self, obj):
        return status_colour(obj.status)

    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage
    account_verification_status_colour.short_description = 'Account Status'  # Set a custom column header
    account_verification_status_colour.admin_order_field = 'account_verification_status'  # Enable sorting by stage
    status_colour.short_description = 'Status'  # Set a custom column header
    status_colour.admin_order_field = 'Status'  # Enable sorting by stage
    # agent_uid.short_description = 'Agent UID'  # Enable sorting by stage

    def has_add_permission(self, request):
        return False


class UserAdmin(CustomModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('user_uid', 'username', 'first_name',
         'last_name', 'mobile', 'email', 'profile_image', 'status')}),
        # ('Permissions', {'fields': ('status', 'user_permissions',)}),
        # ('Activity History', {'fields': ('date_joined', 'last_login')}),
    )

    list_display = ("user_uid", "username", "first_name", "last_name", "email", "mobile", "status_colour")
    list_filter = ("status",)
    search_fields = ("user_uid", "username", "first_name", "last_name", "email", "mobile")

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def status_colour(self, obj):
        return status_colour(obj.status)

    status_colour.short_description = 'Status'  # Set a custom column header
    status_colour.admin_order_field = 'Status'  # Enable sorting by stage


class CountryAdmin(CustomModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    exclude = ("status", "image",)

    def has_add_permission(self, request):
        return True

class StateAdmin(CustomModelAdmin):
    list_display = ("name", "country",)
    search_fields = ("name", "country__name")
    exclude = ("status",)

class CityAdmin(CustomModelAdmin):
    list_display = ("name", "state",)
    search_fields = ("name", "state__name")
    exclude = ("status",)

class InclusionsAdmin(CustomModelAdmin):
    list_display = ("name", "status_colour")
    list_filter = ("status",)
    search_fields = ("name",)
    exclude = ("is_deleted", "package", "activity", "status")

    def status_colour(self, obj):
        return status_colour(obj.status)

    status_colour.short_description = 'Status'  # Set a custom column header
    status_colour.admin_order_field = 'Status'  # Enable sorting by stage

    def get_queryset(self, request):
        # Get the base queryset
        queryset = super().get_queryset(request)
        # Filter the queryset to exclude exclusions with non-null package and activity
        queryset = queryset.filter(package__isnull=True, activity__isnull=True)
        return queryset

class ExclusionsAdmin(CustomModelAdmin):
    list_display = ("name", "status_colour")
    search_fields = ("name",)
    exclude = ("package", "activity", "status")

    def status_colour(self, obj):
        return status_colour(obj.status)

    status_colour.short_description = 'Status'  # Set a custom column header
    status_colour.admin_order_field = 'Status'  # Enable sorting by stage

    def get_queryset(self, request):
        # Get the base queryset
        queryset = super().get_queryset(request)
        # Filter the queryset to exclude exclusions with non-null package and activity
        queryset = queryset.filter(package__isnull=True, activity__isnull=True)
        return queryset


class ActivityAdmin(CustomModelAdmin):
    list_display = ("activity_uid", "agent", "truncated_title", "tour_class",
                    "stage_colour",)
    list_filter = ("tour_class", "stage")
    search_fields = ("title", "agent__agent_uid", "tour_class",
                     "activities__name", "activity_uid")
    exclude = ('is_submitted',)

    fieldsets = (
        (None, {
            'fields': ('stage', 'activity_uid', 'title', 'agent', 'tour_class',
                       'duration', 'duration_day', 'duration_night', 'duration_hour',
                       'min_members', 'max_members', 'pickup_point', 'pickup_time_string', 
                       'drop_point', 'drop_time_string', 'locations',
                       'activities', 'suitable_for', 'is_popular')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(stage='in-progress')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'stage':
            kwargs['choices'] = [('approved', 'Approved'), ('pending', 'Pending'), ('rejected', 'Rejected'),]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # obj is not None, so this is an edit
            return [field.name for field in self.model._meta.fields
                    if field.name not in ['is_submitted', 'stage', 'id', 'updated_on', 'created_on', 'is_popular']
                    ] + ['pickup_time_string', 'drop_time_string', 'locations', 'activities', 'suitable_for']
        else:  # This is an addition
            return [field.name for field in self.model._meta.fields
                    if field.name not in ['is_submitted', 'stage', 'id', 'updated_on', 'created_on']]

    def pickup_time_string(self, obj):
        if obj.pickup_time:
            return obj.pickup_time.strftime('%I:%M %p')
        return None  # Return None if pickup_time is None

    pickup_time_string.short_description = 'Pickup Time'  # Set a custom column header for pickup_string

    def drop_time_string(self, obj):
        if obj.drop_time:
            return obj.drop_time.strftime('%I:%M %p')
        return None  # Return None if drop_time is None

    drop_time_string.short_description = 'Drop Time'  # Set a custom column header for pickup_string


    inlines = [ActivityImageInline, ActivityItineraryInline, ActivityInformationsInline,
               ActivityPricingInline,ActivityCancellationPolicyInline, 
               ActivityFaqQuestionAnswerInline]

    def truncated_title(self, obj):
        # Truncate title to 60 characters using truncatechars filter
        return truncatechars(obj.title, 60)
    truncated_title.short_description = 'Title'
    truncated_title.admin_order_field = 'title'

    def stage_colour(self, obj):
        return stage_colour(obj.stage)

    def status_colour(self, obj):
        return status_colour(obj.status)

    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage
    status_colour.short_description = 'Status'  # Set a custom column header
    status_colour.admin_order_field = 'Status'  # Enable sorting by stage

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class AttractionAdmin(CustomModelAdmin):
    list_display = ("truncated_title",)
    search_fields = ("title",)
    exclude = ("status",)
    inlines = [AttractionImageInline]

    def status_colour(self, obj):
        return status_colour(obj.status)

    def truncated_title(self, obj):
        # Truncate title to 60 characters using truncatechars filter
        return truncatechars(obj.title, 150)
    truncated_title.short_description = 'Title'
    truncated_title.admin_order_field = 'title'

    # def truncated_overview(self, obj):
    #     # Truncate title to 60 characters using truncatechars filter
    #     return truncatechars(obj.overview, 450)
    # truncated_overview.short_description = 'overview'
    # truncated_overview.admin_order_field = 'overview'

    status_colour.short_description = 'Status'  # Set a custom column header
    status_colour.admin_order_field = 'Status'  # Enable sorting by stage


class PackageAdmin(CustomModelAdmin):
    list_display = ("package_uid", "agent", "truncated_title", "tour_class",
                    "stage_colour",)
    list_filter = ("tour_class", "stage")
    search_fields = ("title", "agent__agent_uid", "agent__first_name",
                     "activities__name", "tour_class", "package_uid")
    exclude = ('is_submitted',)

    fieldsets = (
        (None, {
            'fields': ('stage', 'package_uid', 'title', 'agent', 'tour_class',
                       'duration', 'duration_day', 'duration_night', 'duration_hour',
                       'min_members', 'max_members', 'pickup_point', 'pickup_time_string', 
                       'drop_point', 'drop_time_string', "locations",
                       'activities', 'suitable_for', 'is_popular')
        }),
    )
    
    inlines = [
        PackageImageInline, ItineraryInline, InclusionExclusionInline, InformationsInline,
        PricingInline, CancellationPolicyInline, PackageFaqQuestionAnswerInline,
        ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.exclude(stage='in-progress')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'stage':
            kwargs['choices'] = [('approved', 'Approved'), ('pending', 'Pending'), ('rejected', 'Rejected'),]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # obj is not None, so this is an edit
            return [field.name for field in self.model._meta.fields
                    if field.name not in ['is_submitted', 'stage', 'id', 'updated_on', 'created_on', 'is_popular']
                    ] + ['pickup_time_string', 'drop_time_string', 'locations', 'suitable_for', 'activities']
        else:  # This is an addition
            return [field.name for field in self.model._meta.fields
                    if field.name not in ['is_submitted', 'stage', 'id', 'updated_on', 'created_on']]

    def pickup_time_string(self, obj):
        if obj.pickup_time:
            return obj.pickup_time.strftime('%I:%M %p')
        return None  # Return None if pickup_time is None

    pickup_time_string.short_description = 'Pickup Time'  # Set a custom column header for pickup_string

    def drop_time_string(self, obj):
        if obj.drop_time:
            return obj.drop_time.strftime('%I:%M %p')
        return None  # Return None if drop_time is None

    drop_time_string.short_description = 'Drop Time'  # Set a custom column header for pickup_string

    def truncated_title(self, obj):
        # Truncate title to 60 characters using truncatechars filter
        return truncatechars(obj.title, 60)
    truncated_title.short_description = 'Title'
    truncated_title.admin_order_field = 'title'

    def stage_colour(self, obj):
        return stage_colour(obj.stage)

    def status_colour(self, obj):
        return status_colour(obj.status)

    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage
    status_colour.short_description = 'Status'  # Set a custom column header
    status_colour.admin_order_field = 'Status'  # Enable sorting by stage

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class PricingDateFilter(admin.SimpleListFilter):
    title = _('Pricing Date Range')
    parameter_name = 'pricing_date_range'

    def lookups(self, request, model_admin):
        months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]  # Generating month names
        return months 
    
    def queryset(self, request, queryset):
        if self.value() in [str(i) for i in range(1, 13)]:
            return queryset.filter(tour_date__month=int(self.value()))
            # return queryset.filter(package__pricing_package__start_date__month=int(self.value()))
        

class BookingAdmin(CustomModelAdmin):
    list_display = ("booking_id", "display_created_on", "tour_date", "user_uid",
                    "package_uid", "activity_uid", "agent_id","booking_status_colour",)
    list_filter = ("booking_status",PricingDateFilter,)  # Add the custom filter

    search_fields = ("booking_id", "created_on", "user__user_uid", "tour_date",
                     "package__package_uid", "activity__activity_uid", "package__agent__agent_uid",
                     "activity__agent__agent_uid")
    exclude = ("status",)    

    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            if obj.activity:
                return (
                    (None, {
                        'fields': ('user','booking_id', 'activity_uid', 'activity_name', 
                                'agent_id','agent','order_id','booking_type','booking_amount','payment_id',
                                'booking_status','display_created_on','tour_date', 
                                    'adult', 'child', 'infant', 'refund_amount')
                    }),
            ('Pricing', {
                'fields': ('pricing_section',),
            }),
                )
            else:
                return (
                    (None, {
                        'fields': ('user','booking_id', 'package_uid', 'package_name', 
                               'agent_id','agent','order_id','booking_type','booking_amount','payment_id',
                               'booking_status','display_created_on','tour_date', 
                                'adult', 'child', 'infant', 'refund_amount','object_id')
                }),
        ('Pricing', {
            'fields': ('pricing_section',),
        }),
            )
        else:  # Add page
            return (
                (None, {
                    'fields': ('user', 'package', 'activity', 
                               'adult', 'child', 'infant', 'booking_amount', 
                               'order_id', 'payment_id', 'booking_status','tour_date', 'end_date',
                               'refund_amount', 'pricing','is_trip_completed')
                }),
            )


    def pricing_section(self, obj):
        pricing_obj = obj.pricing
        if pricing_obj:
            pricing_dict = {'Tour Date': pricing_obj.start_date, 'Adults Rate': obj.adults_rate,
                            'Child Rate': obj.child_rate,'Infant Rate': obj.infant_rate,
                            }

            # Render the HTML template with pricing_list
            pricing_info = render_to_string('admin/pricing_table_template.html', {'pricing_dict': pricing_dict})
            return mark_safe(pricing_info)  # Mark the string as safe HTML
        else:
            return "No pricing information available."

    pricing_section.short_description = ""

    def agent(self, obj):
        return obj.package.agent.username if obj.package else None
    
    def agent_id(self, obj):
        if obj.package:
            return obj.package.agent.agent_uid
        elif obj.activity:
            return obj.activity.agent.agent_uid
        else:
            return None

    def user_uid(self, obj):
        return obj.user.user_uid if obj.user else None

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"

    def activity_uid(self, obj):
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"

    def display_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
    display_created_on.short_description = "Booking date"

    def package_name(self, obj):
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"

    def activity_name(self, obj):
        return truncatechars(obj.activity.title if obj.activity else None, 35)
    activity_name.short_description = "Activity Name"

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     self.readonly_fields += ('display_created_on', 'package_name')
    #     return super().change_view(request, object_id, form_url, extra_context)

    def booking_status_colour(self, obj):
        return booking_status_colour(obj.booking_status)

    booking_status_colour.short_description = 'Booking Status'  # Set a custom column header
    booking_status_colour.admin_order_field = 'Booking Status'  # Enable sorting by stage

    agent.admin_order_field = 'package__agent__username' 
    agent_id.admin_order_field = 'package__agent__agent_uid'  
    agent_id.short_description = 'Agent UID'  # Set a custom column header
    display_created_on.admin_order_field = 'created_on'  # Enable sorting by created_on
    package_name.admin_order_field = 'Package Name'  # Enable sorting by stage
    user_uid.admin_order_field = 'User UID'  # Enable sorting by user_uid
    package_uid.admin_order_field = 'User UID'  # Enable sorting by user_uid
    activity_uid.admin_order_field = 'User UID'  # Enable sorting by user_uid

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.exclude(booking_status='PENDING').order_by('-tour_date')
        return queryset
    
    


# class TransactionAdmin(CustomModelAdmin):
#     def get_fieldsets(self, request, obj=None):
#         if obj:  # Detail page
#             return (
#                 (None, {
#                     'fields': ('transaction_uid','booking_uid', 'user', 'package_name',
#                                'package_uid', 'agent', 'agent_uid', 'display_created_on',
#                                 'refund_status', 'refund_amount',)
#                 }),
#             )
#         else:  # Add page
#             return (
#                 (None, {
#                     'fields': ('package', 'booking', 'refund_status', 'refund_amount', 'user',)
#                 }),
#             )
        
#     list_display = ("transaction_uid", "booking_uid", "user","package_name", "package_uid",
#                      "agent", "agent_uid","refund_status", "display_created_on",)
#     list_filter = ("refund_status",)
#     search_fields = ("refund_status","transaction_uid","user")
#     exclude = ('status',)

#     def agent(self, obj):
#         return obj.package.agent.username if obj.package else None
    
#     def agent_uid(self, obj):
#         return obj.package.agent.agent_uid if obj.package else None

#     def package_uid(self, obj):
#         return obj.package.package_uid if obj.package else None
#     package_uid.short_description = "Package UID"

#     def package_name(self, obj):
#         return obj.package.title if obj.package else None
#     package_name.short_description = "Package Name"

#     def booking_uid(self, obj):
#         return obj.booking.booking_id if obj.booking else None
#     booking_uid.short_description = "Booking UID"

#     def display_created_on(self, obj):
#         return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
#     display_created_on.short_description = "Transaction date"

#     def has_add_permission(self, request, obj=None):
#         return True

#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         self.readonly_fields += ('transaction_uid', 'agent_uid', 'package_uid', 'booking_uid', 'agent',
#                                  'display_created_on', 'package_name')
#         return super().change_view(request, object_id, form_url, extra_context)
    
#     def save_model(self, request, obj, form, change):

#         # Get the original object before saving changes
#         original_obj = self.model.objects.get(pk=obj.pk) if change else None
        
#         print(original_obj)
#         # Save the changes
#         super().save_model(request, obj, form, change)

#         # Check if refund_status has changed and the new status is either "CANCELLED" or "REFUNDED"
#         if change and obj.refund_status in ['CANCELLED', 'REFUNDED'] and obj.refund_status != original_obj.refund_status:
#             print("hi2")
#             if obj.refund_status == 'REFUNDED':
#                 Booking.objects.filter(id=obj.booking_id).update(booking_status=obj.refund_status)
#             elif obj.refund_status == 'CANCELLED':
#                 Booking.objects.filter(id=obj.booking_id).update(booking_status='FAILED')


#             subject = f"REFUND STATUS"
#             message = f"Dear {obj.user.username},\n\nYour Booking has been {obj.refund_status}."
#             send_email.delay(subject,message,obj.user.email)


class UserRefundTransactionAdmin(CustomModelAdmin):
    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            if obj.activity:
                return (
                    (None, {
                        'fields': ('user', 'refund_uid','booking_uid', "booking_amount","booking_date",
                                'activity_uid', 'activity_name', 'agent', 'agent_uid', 'display_created_on',
                                    'refund_status', 'refund_amount')
                    }),
                    ('Cancellation policy', {
                        'fields': ('cancellation_policies',)
                    }),
                )
            else:
                return (
                    (None, {
                        'fields': ('user', 'refund_uid','booking_uid', "booking_amount","booking_date",
                                'package_uid', 'package_name', 'agent', 'agent_uid', 'display_created_on',
                                    'refund_status', 'refund_amount')
                    }),
                    ('Cancellation policy', {
                        'fields': ('cancellation_policies',)
                    }),
                )
        else:  # Add page
            return (
                (None, {
                    'fields': ('package', 'activity', 'booking', 'refund_status', 'refund_amount', 'user',)
                }),
            )
        
    list_display = ("refund_uid", "booking_uid", "user","refund_amount", "package_uid", "activity_uid",
                     "agent", "agent_uid","refund_status_colour", "display_created_on",)
    
    list_filter = ("refund_status",)
    search_fields = ("refund_uid", "booking__booking_id", "user__user_uid",
                     "user__username", "refund_amount", "package__title",
                     "package__package_uid", "activity__activity_uid",
                     "package__agent__username", "activity__agent__username",
                     "package__agent__agent_uid", "activity__agent__agent_uid", "created_on")
    exclude = ('status',)

    def cancellation_policies(self, obj):
        cancellation_categories = []
        
        if obj.package:
            policies = CancellationPolicy.objects.filter(package=obj.package)
            for policy in policies:
                categories = policy.category.all()
                for category in categories:
                    if category.to_day == 0:
                        category_dict = {
                            'from_day': category.from_day,
                            'amount_percent': category.amount_percent,
                            }
                    else:
                        category_dict = {
                            'from_day': category.from_day,
                            'to_day': category.to_day,
                            'amount_percent': category.amount_percent,
                            }
                    cancellation_categories.append(category_dict)

        if obj.activity:
            policies = ActivityCancellationPolicy.objects.filter(activity=obj.activity)
            for policy in policies:
                categories = policy.category.all()
                cancellation_categories = []
                for category in categories:
                    if category.to_day == 0:
                        category_dict = {
                            'from_day': category.from_day,
                            'amount_percent': category.amount_percent,
                            }
                    else:
                        category_dict = {
                            'from_day': category.from_day,
                            'to_day': category.to_day,
                            'amount_percent': category.amount_percent,
                            }

                    cancellation_categories.append(category_dict)

        if not cancellation_categories:
            return "No cancellation policies available."
        
        # Render the HTML template with pricing_list
        cancellation_info = render_to_string('admin/cancellation_table_template.html', {'cancellation_category': cancellation_categories})
        return mark_safe(cancellation_info)  # Mark the string as safe HTML
    
    cancellation_policies.short_description = ""

    def agent(self, obj):
        if obj.package:
            return obj.package.agent.username
        elif obj.activity:
            return obj.activity.agent.username
        else:
            return None

    def agent_uid(self, obj):
        if obj.package:
            return obj.package.agent.agent_uid
        elif obj.activity:
            return obj.activity.agent.agent_uid
        else:
            return None

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"

    def activity_uid(self, obj):
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"

    def package_name(self, obj):
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"
    
    def activity_name(self, obj):
        return truncatechars(obj.activity.title if obj.activity else None, 35)
    activity_name.short_description = "Activity Name"

    def booking_uid(self, obj):
        return obj.booking.booking_id if obj.booking else None
    booking_uid.short_description = "Booking UID"

    def booking_amount(self, obj):
        return obj.booking.booking_amount if obj.booking else None
    booking_amount.short_description = "Booking amount"

    def booking_date(self, obj):
        return obj.created_on.strftime("%Y-%m-%d") if obj.booking else None
    booking_date.short_description = "Booking date"

    def display_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
    display_created_on.short_description = "Transaction Date"

    def has_add_permission(self, request, obj=None):
        return False
    
    # def calculate_refund_amount(self, obj):
    #     print("g1")
    #     if obj.booking and obj.booking.package:
    #         print("z1")
    #         booking_date = obj.booking.created_on

    #         print(obj.booking.package.id)
    #         print(obj.package.id)
    #         policies = CancellationPolicy.objects.filter(package_id=obj.package.id)
    #         refund_amount = obj.booking.booking_amount

    #         print(booking_date)
    #         print(policies)
    #         for policy in policies:
    #             if policy.from_day <= (booking_date - obj.created_on).days <= policy.to_day:
    #                 print("k`1")
    #                 amount_percent = Decimal(policy.amount_percent)
    #                 refund_amount = refund_amount - (refund_amount * (amount_percent / Decimal(100)))
    #                 print(refund_amount)
    #                 return refund_amount
                
    #     return None

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.readonly_fields += ('refund_uid', 'agent_uid', 'package_uid', 'booking_uid',"booking_date", 'agent',
                                 'display_created_on', 'package_name','booking_amount','cancellation_policies','user',
                                 'activity_uid', 'activity_name')
        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):

        # Get the original object before saving changes
        original_obj = self.model.objects.get(pk=obj.pk) if change else None
        # Save the changes
        super().save_model(request, obj, form, change)

        # Check if refund_status has changed and the new status is either "CANCELLED" or "REFUNDED"
        if change and obj.refund_status in ['CANCELLED', 'REFUNDED'] and obj.refund_status != original_obj.refund_status:
            if obj.refund_status == 'REFUNDED':
                Booking.objects.filter(id=obj.booking_id).update(booking_status=obj.refund_status)
            elif obj.refund_status == 'CANCELLED':
                Booking.objects.filter(id=obj.booking_id).update(booking_status='FAILED')


            subject = f"REFUND STATUS"
            message = f"Dear {obj.user.username},\n\nYour Booking has been {obj.refund_status}."
            send_email.delay(subject,message,obj.user.email)


    def refund_status_colour(self, obj):
        return refund_status_colour(obj.refund_status)

    refund_status_colour.short_description = 'Refund Status'  # Set a custom column header
    refund_status_colour.admin_order_field = 'Refund Status'  # Enable sorting by stage

    booking_uid.admin_order_field = 'Booking UID'  # Enable sorting by stage
    package_name.admin_order_field = 'Package Name'  # Enable sorting by stage
    package_uid.admin_order_field = 'Package UID'  # Enable sorting by stage
    activity_uid.admin_order_field = 'Activity UID'  # Enable sorting by stage
    agent.admin_order_field = 'Agent'  # Enable sorting by stage
    agent_uid.admin_order_field = 'Agent UID'  # Enable sorting by stage
    agent_uid.short_description = 'Agent UID'  # Set a custom column header
    display_created_on.admin_order_field = 'Transaction Date'  # Enable sorting by stage


class AgentTransactionSettlementAdmin(CustomModelAdmin):
    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            if obj.activity:
                return (
                    (None, {
                        'fields': ('agent_uid','transaction_id','booking_uid', "booking_amount",
                                "booking_type", 'activity_uid', 'activity_name', 'payment_settlement_status',
                                'payment_settlement_amount','payment_settlement_date',)
                    }),
                    ('Pricing', {
                        'fields': ('pricing_section',),
                    }),
                    ('Cancellation Policy', {
                        'fields': ('cancellation_policies',),
                    }),
                )
            else:
                return (
                    (None, {
                        'fields': ('agent_uid','transaction_id','booking_uid', "booking_amount",
                                "booking_type", 'package_uid', 'package_name', 'payment_settlement_status',
                                'payment_settlement_amount','payment_settlement_date',)
                    }),
                    ('Pricing', {
                        'fields': ('pricing_section',),
                    }),
                    ('Cancellation Policy', {
                        'fields': ('cancellation_policies',)
                    }),
                )
        else:  # Add page
            return (
                (None, {
                    'fields': ('package', 'activity', 'booking', 'payment_settlement_status',
                                'payment_settlement_amount', 'agent','payment_settlement_date')
                }),
            )
        
    list_display = ("transaction_id", "booking_uid","booking_type", "package_uid", "activity_uid", "agent_uid",
                    "payment_settlement_date", "payment_settlement_status_colour", 'account_verification_status')
    
    list_filter = ("payment_settlement_status","booking_type")
    search_fields = ("transaction_id", "booking__booking_id", "booking_type", "package__title",
                     "package__package_uid", "activity__activity_uid", "agent__agent_uid",
                     "agent__username", "payment_settlement_date")
    exclude = ('status',)

    def account_verification_status(self, obj):
        return account_verification_status_colour(obj.agent.account_verification_status if obj.agent else None)
    account_verification_status.short_description = "Account Status"
    account_verification_status.admin_order_field = "Account Status"

    def pricing_section(self, obj):
        pricing_obj = obj.booking.pricing
        if pricing_obj:
            if obj.booking.adults_rate:
                pricing_dict = {'Tour Date': obj.booking.tour_date, 
                                'Adult Count':obj.booking.adult,
                                'Adult Rate': obj.booking.adults_rate,
                                'Adult Commission': obj.booking.adults_commission,
                                'Child Count':obj.booking.child,
                                'Child Rate': obj.booking.child_rate,
                                'Child Commission': obj.booking.child_commission, 
                                'Infant Count':obj.booking.infant,
                                'Infant Rate': obj.booking.infant_rate,
                                'Infant Commission': obj.booking.infant_commission,
                                }
            

            # Render the HTML template with pricing_list
            pricing_info = render_to_string('admin/pricing_table_template.html', {'pricing_dict': pricing_dict})
            return mark_safe(pricing_info)  # Mark the string as safe HTML
        else:
            return "No pricing information available."

    pricing_section.short_description = ""

    def cancellation_policies(self, obj):
        cancellation_categories = []
        
        if obj.package:
            policies = CancellationPolicy.objects.filter(package=obj.package)
            formatted_policies = ""
            for policy in policies:
                categories = policy.category.all()
                for category in categories:
                    if category.to_day == 0:
                        category_dict = {
                            'from_day': category.from_day,
                            'amount_percent': category.amount_percent,
                            }
                    else:
                        category_dict = {
                            'from_day': category.from_day,
                            'to_day': category.to_day,
                            'amount_percent': category.amount_percent,
                            }

                    cancellation_categories.append(category_dict)

        if obj.activity:
            policies = ActivityCancellationPolicy.objects.filter(activity=obj.activity)
            formatted_policies = ""
            for policy in policies:
                categories = policy.category.all()
                cancellation_categories = []
                for category in categories:
                    if category.to_day == 0:
                        category_dict = {
                            'from_day': category.from_day,
                            'amount_percent': category.amount_percent,
                            }
                    else:
                        category_dict = {
                            'from_day': category.from_day,
                            'to_day': category.to_day,
                            'amount_percent': category.amount_percent,
                            }

                    cancellation_categories.append(category_dict)

        if not cancellation_categories:
            return "No cancellation policies available."
        
        # Render the HTML template with pricing_list
        cancellation_info = render_to_string('admin/cancellation_table_template.html', {'cancellation_category': cancellation_categories})
        return mark_safe(cancellation_info)  # Mark the string as safe HTML

    cancellation_policies.short_description = ''
    def agent(self, obj):
        return obj.package.agent.username if obj.package else None
    
    def agent_uid(self, obj):
        if obj.package:
            return obj.package.agent.agent_uid
        elif obj.activity:
            return obj.activity.agent.agent_uid
        else:
            return None

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"

    def activity_uid(self, obj):
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"

    def package_name(self, obj):
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"

    def activity_name(self, obj):
        return truncatechars(obj.activity.title if obj.activity else None, 35)
    activity_name.short_description = "Activity Name"

    def booking_uid(self, obj):
        return obj.booking.booking_id if obj.booking else None
    booking_uid.short_description = "Booking UID"

    def booking_amount(self, obj):
        return obj.booking.booking_amount if obj.booking else None
    booking_amount.short_description = "Booking amount"

    def booking_type(self, obj):
        return obj.booking.booking_type if obj.booking else None
    booking_amount.short_description = "Booking type"

    def display_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
    display_created_on.short_description = "Transaction date"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Overriding default change view to make readonly fields and
        check agent bank approved status and show message if not approved
        and restrict editing fields.
        """
        # Get the object based on the object_id
        obj = self.get_object(request, object_id)
        
        # Define the initial set of read-only fields
        self.readonly_fields = ['transaction_id', 'agent_uid', 'package_uid', 'booking_uid', 'agent',
                                'display_created_on', 'package_name','booking_amount', 'booking_type',
                                'cancellation_policies','pricing_section', 'activity_uid', 'activity_name']

        # Check if the object exists and if the agent's account verification status is not approved
        if obj and obj.agent and obj.agent.account_verification_status != 'approved':
            # Add additional read-only fields if the condition is met
            self.readonly_fields += ['payment_settlement_status',
                                     'payment_settlement_amount',
                                     'payment_settlement_date']
            # Display error message when agent bank account is not approved
            messages.error(request, "Bank Account Not verified.")

        # Call the parent class's change_view method
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):

        # Get the original object before saving changes
        original_obj = self.model.objects.get(pk=obj.pk) if change else None
        # Save the changes
        super().save_model(request, obj, form, change)

        if change and obj.payment_settlement_status in ['SUCCESSFUL'] and obj.payment_settlement_status != original_obj.payment_settlement_status:
            obj.transaction_id = f"EWTRAN-{obj.id}"
            obj.save()

        subject = f"EXPLORE WORLD | TRANSACTION"
        message = f"Dear {obj.agent.agent_uid},\n\nYour transaction settlement has been {obj.payment_settlement_status}."
        send_email.delay(subject,message,obj.agent.email)

    def payment_settlement_status_colour(self, obj):
        return refund_status_colour(obj.payment_settlement_status)

    payment_settlement_status_colour.short_description = 'Payment settlement status'  # Set a custom column header
    payment_settlement_status_colour.admin_order_field = 'Payment settlement status'  # Enable sorting by stage

    booking_uid.admin_order_field = 'Booking UID'  # Enable sorting by stage
    package_name.admin_order_field = 'Package Name'  # Enable sorting by stage
    package_uid.admin_order_field = 'Package UID'  # Enable sorting by stage
    activity_uid.admin_order_field = 'Activity UID'  # Enable sorting by stage
    agent_uid.admin_order_field = 'Agent UID'  # Enable sorting by stage
    agent_uid.short_description = 'Agent UID'  # Set a custom column header
    display_created_on.admin_order_field = 'Transaction Date'  # Enable sorting by stage

    def has_add_permission(self, request, obj=None):
        return False


class UserReviewAdmin(CustomModelAdmin):
    list_display = ("user", "package_uid", "activity_uid", "rating")
    search_fields = ( "package__package_uid", "activity__activity_uid", "user__user_uid")
    list_filter = ("rating",)
    exclude = ('status', 'is_deleted', 'is_active')
    readonly_fields = ("package_uid","activity_name","package_name")
    fieldsets = (
        (None, {
            'fields': ("user", "package","rating", "review",
                       "booking", "agent", "agent_comment",)
        }),
        )

    inlines = [UserReviewImageInline]

    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            if obj.activity:
                return (
                    (None, {
                        'fields': ("user", "activity_uid", "activity_name", "rating", "review",
                                "booking", "agent", "agent_comment",)
                    }),
                )
            else:
                return (
                    (None, {
                        'fields': ("user", "package_uid", "package_name", "rating", "review",
                                "booking", "agent", "agent_comment",)
                    }),
                )
        else:  # Add page
            return (
        (None, {
            'fields': ("user", "package", "rating", "review",
                       "booking", "agent", "agent_comment",)
        }),
            )

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"

    def activity_uid(self, obj):
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"

    def package_name(self, obj):
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"

    def activity_name(self, obj):
        return truncatechars(obj.activity.title if obj.activity else None, 35)
    activity_name.short_description = "Activity Name"

    activity_uid.admin_order_field = 'Activity UID'  # Enable sorting by user_uid
    package_uid.admin_order_field = 'Package UID'  # Enable sorting by user_uid


    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


class AdvanceAmountPercentageSettingAdmin(CustomModelAdmin):
    list_display = ("id","percentage")
    search_fields = ( "id", "percentage")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True

class PackageCategoryAdmin(CustomModelAdmin):
    list_display = ("name",)
    search_fields = ( "name",)
    exclude = ('status',)

def dashboard_page(request):

    total_user_count = User.objects.count()

    #Booking
    total_bookings_count = Booking.objects.count()
    successful_bookings = Booking.objects.filter(booking_status='SUCCESSFUL').count()
    failed_bookings = Booking.objects.filter(booking_status='FAILED').count()
    refunded_bookings = Booking.objects.filter(booking_status='REFUNDED').count()

    #Agents
    total_agent_count = Agent.objects.count()
    pending_agents = Agent.objects.filter(stage='pending').count()
    approved_agents = Agent.objects.filter(stage='approved').count()
    rejected_agents = Agent.objects.filter(stage='rejected').count()

    #Agent Transactions
    total_agent_transaction_count = AgentTransactionSettlement.objects.count()
    successful_agent_transaction_count = AgentTransactionSettlement.objects.filter(payment_settlement_status='SUCCESSFUL').count()
    rejected_agent_transaction_count = AgentTransactionSettlement.objects.filter(payment_settlement_status='REJECTED').count()
    pending_agent_transaction_count = AgentTransactionSettlement.objects.filter(payment_settlement_status='PENDING').count()

    #User Transactions
    total_user_transaction_count = UserRefundTransaction.objects.count()
    refunded_user_transaction_count = UserRefundTransaction.objects.filter(refund_status='REFUNDED').count()
    rejected_user_transaction_count = UserRefundTransaction.objects.filter(refund_status='REJECTED').count()
    pending_user_transaction_count = UserRefundTransaction.objects.filter(refund_status='PENDING').count()

    cards = {
        'total_bookings_count': total_bookings_count,
        'total_agent_count': total_agent_count,
        'total_user_count': total_user_count,
        'successful_bookings':successful_bookings,
        'failed_bookings':failed_bookings,
        'refunded_bookings':refunded_bookings,
        'pending_agents':pending_agents,
        'approved_agents':approved_agents,
        'rejected_agents':rejected_agents,
        'total_agent_transaction_count':total_agent_transaction_count,
        'successful_agent_transaction_count':successful_agent_transaction_count,
        'rejected_agent_transaction_count':rejected_agent_transaction_count,
        'pending_agent_transaction_count':pending_agent_transaction_count,
        'total_user_transaction_count':total_user_transaction_count,
        'refunded_user_transaction_count':refunded_user_transaction_count,
        'rejected_user_transaction_count':rejected_user_transaction_count,
        'pending_user_transaction_count':pending_user_transaction_count
    }

    current_year = datetime.now().year

    months = [calendar.month_name[i] for i in range(1, 13)]

    month_abbreviations = {'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr', 'May': 'May', 'June': 'Jun', 'July': 'Jul',
                            'August': 'Aug', 'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'}

    bar_graph_selected_year = request.GET.get('bar_graph_year', current_year)
    if bar_graph_selected_year:
        bar_graph_selected_year = int(bar_graph_selected_year)
        bar_graph_start_date = datetime(bar_graph_selected_year, 1, 1)
        bar_graph_end_date = datetime(bar_graph_selected_year, 12, 31)

        # Filter bookings based on agent_status if provided in the URL
        agent_stage_filter = request.GET.get('agent_stage_status')
        if agent_stage_filter:
            bookings_count_by_month = Agent.objects.filter(
                created_on__range=[bar_graph_start_date, bar_graph_end_date], stage=agent_stage_filter
            ).values('created_on__month').annotate(count=Count('id'))
        else:
            # Use the original query if no filter is provided
            bookings_count_by_month = Agent.objects.filter(
                created_on__range=[bar_graph_start_date, bar_graph_end_date]
            ).values('created_on__month').annotate(count=Count('id'))

        agent_chart_booking = [
            {
                'month': calendar.month_name[item['created_on__month']],
                'count': item['count']
            }
            for item in bookings_count_by_month
        ]

        agent_month_counts = {item['month']: item['count'] for item in agent_chart_booking}

        # Populate barchart_booking with counts for all months
        agent_chart_booking = [
            {'month': month, 'count': agent_month_counts.get(month, 0)}
            for month in months
        ]

    selected_year = request.GET.get('year',current_year)
    if selected_year:
        selected_year = int(selected_year)
        start_date = datetime(selected_year, 1, 1)
        end_date = datetime(selected_year, 12, 31)

     
        # Filter bookings based on booking_status if provided in the URL
        booking_status_filter = request.GET.get('booking_status')
        if booking_status_filter:
            bookings_count_by_month = Booking.objects.filter(
                created_on__range=[start_date, end_date], booking_status=booking_status_filter
            ).values('created_on__month').annotate(count=Count('id'))
        else:
            # Use the original query if no filter is provided
            bookings_count_by_month = Booking.objects.filter(
                created_on__range=[start_date, end_date]
            ).values('created_on__month').annotate(count=Count('id'))

        barchart_booking = [
            {
                'month': calendar.month_name[item['created_on__month']],
                'count': item['count']
            }
            for item in bookings_count_by_month
        ]

        month_counts = {item['month']: item['count'] for item in barchart_booking}

        # Populate barchart_booking with counts for all months
        barchart_booking = [
            {'month': month, 'count': month_counts.get(month, 0)}
            for month in months
        ]

    # Create list of years for year filter
    current_year = date.today().year
    years_list = [str(year) for year in range(current_year, current_year - 11, -1)]
    
    for month_dict in barchart_booking:
        month_dict['month'] = month_abbreviations[month_dict['month']]
    for month_dict in agent_chart_booking:
        month_dict['month'] = month_abbreviations[month_dict['month']]

    context = {'cards':cards,
                'barchart_booking':barchart_booking,
                'agent_chart_booking': agent_chart_booking,
                'years_list': years_list}

    admin_site: AdminSite = site
    context_data = admin_site.each_context(request)

    # Initialize an empty list to store the reordered available apps
    reordered_available_apps = []

    # Create a dictionary to map model names to their positions in ADMIN_REORDER
    model_order_map = {}
    for idx, item in enumerate(ADMIN_REORDER):
        for model_name in item['models']:
            model_order_map[model_name] = idx

    # Iterate through the ADMIN_REORDER settings
    for item in ADMIN_REORDER:
        # Get the app_label and models for the current item
        models = item['models']

        # Find the corresponding available app using app_label
        for available_app in context_data['available_apps']:
            # Filter and reorder models for the current app based on the models in the ADMIN_REORDER setting
            reordered_models = []
            for model_name in models:
                for model_info in available_app['models']:
                    model_class = model_info['model']
                    current_model_name = f"{model_class._meta.app_label}.{model_class.__name__}"
                    if current_model_name == model_name:
                        reordered_models.append(model_info)
                        break 

            reordered_available_apps.append({
                'name': item['label'],
                'app_label': item['app'],
                'app_url': '/admin/api/',
                'has_module_perms': True,
                'models': reordered_models
            })
            break

    context_data['available_apps'] = reordered_available_apps

    # Update the context with the modified context data
    context.update(**context_data)
    return render(request, 'admin/admin_dashboard.html', context=context)

from django import forms

class CoverPageInputForm(forms.ModelForm):
    class Meta:
        model = CoverPageInput
        fields = "__all__"

    def clean_satisfaction(self):
        satisfaction = self.cleaned_data.get('satisfaction')
        if satisfaction is not None and not (0 <= satisfaction <= 100):
            raise ValidationError(
                _('Satisfaction must be a decimal number between 0 and 100.'),
                code='invalid'
            )
        return satisfaction


class CoverPageInputAdmin(CustomModelAdmin):
    list_display = ("id", "experience", "clients", "satisfaction")

    fieldsets = (
        (None, {
            'fields': ("experience", "clients", "satisfaction")
        }),
        ('Cover Images', {
            'fields': ("activity_image", "package_image", "attraction_image","product_image")
        }),
        # ('Filters', {
        #     'fields': ('price_min','price_max')
        # }),
    )
    form = CoverPageInputForm

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return True


class SendEnquiryAdmin(CustomModelAdmin):
    list_display = ("id","package_uid", "activity_uid", "name", "email")
    search_fields = ("package__package_uid", "activity__activity_uid", "name", "email")

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"
    package_uid.admin_order_field = 'Package UID'  # Enable sorting by package_uid

    def activity_uid(self, obj):
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"
    # activity_uid.admin_order_field = "Activity UID"  # Enable sorting by activity_uid


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True
    
    def has_change_permission(self, request, obj=None):
        return False


class SuitableForAdmin(CustomModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

class CurrencyAdmin(CustomModelAdmin):
    list_display = ("name",)
    exclude = ('status',)



class BlogsAdmin(admin.ModelAdmin):
    ...
    inlines = [BlogImageInline]


# Unregister model
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)

admin.site.register(User, UserAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Attraction, AttractionAdmin)
admin.site.register(Inclusions, InclusionsAdmin)
admin.site.register(Exclusions, ExclusionsAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Booking,BookingAdmin)
# admin.site.register(Transaction,TransactionAdmin)

admin.site.register(PackageCategory,PackageCategoryAdmin)
admin.site.register(Currency,CurrencyAdmin)
admin.site.register(UserReview,UserReviewAdmin)

admin.site.register(CancellationPolicy)
admin.site.register(PackageCancellationCategory)
admin.site.register(ActivityCancellationCategory)
admin.site.register(ActivityCancellationPolicy)
admin.site.register(CoverPageInput, CoverPageInputAdmin)
admin.site.register(Itinerary)
admin.site.register(SuitableFor, SuitableForAdmin)
admin.site.register(SendEnquiry,SendEnquiryAdmin)

admin.site.register(Pricing)
admin.site.register(BlogCategory)
admin.site.register(BlogImage)
admin.site.register(Blogs,BlogsAdmin)






admin.site.register(AdvanceAmountPercentageSetting,AdvanceAmountPercentageSettingAdmin)


admin.site.register(AgentTransactionSettlement,AgentTransactionSettlementAdmin)
admin.site.register(UserRefundTransaction,UserRefundTransactionAdmin)
