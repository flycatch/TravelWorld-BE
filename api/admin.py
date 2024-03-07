from decimal import Decimal
from django.http import JsonResponse

from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.defaultfilters import truncatewords
from django.utils.html import format_html
from django.template.defaultfilters import truncatechars

from rest_framework.authtoken.models import TokenProxy

from api.common.custom_admin import *
from api.models import *
from api.tasks import *
from api.utils.admin import stage_colour, status_colour, booking_status_colour, refund_status_colour
from django.shortcuts import render
from datetime import datetime
from django.db.models import Case, CharField, Count, F, Subquery, Value, When
import calendar

class AgentAdmin(CustomModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('agent_uid', 
         'agent_name', 'username', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('status', 'stage')}),
        # ('Activity History', {'fields': ('date_joined', 'last_login')}),
    )

    list_display = ("agent_uid", "username", "agent_name", "email", "phone", "status_colour", "stage_colour")
    list_filter = ("status", "stage")
    search_fields = ("agent_uid", "username", "agent_name", "email", "phone")
    readonly_fields = ("agent_uid", "username", "agent_name","email", "phone", "profile_image",)

    def stage_colour(self, obj):
        return stage_colour(obj.stage)

    def status_colour(self, obj):
        return status_colour(obj.status)

    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage
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
    search_fields = ("user_uid", "username", "first_name", "email", "mobile")

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
        return False

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
    exclude = ("is_deleted", "package", "activity")

    def status_colour(self, obj):
        return status_colour(obj.status)

    status_colour.short_description = 'Status'  # Set a custom column header
    status_colour.admin_order_field = 'Status'  # Enable sorting by stage


class ExclusionsAdmin(CustomModelAdmin):
    list_display = ("name", "status_colour")
    list_filter = ("status",)
    search_fields = ("name",)
    exclude = ("package", "activity")

    def status_colour(self, obj):
        return status_colour(obj.status)

    status_colour.short_description = 'Status'  # Set a custom column header
    status_colour.admin_order_field = 'Status'  # Enable sorting by stage


class ActivityAdmin(CustomModelAdmin):
    list_display = ("agent", "truncated_title", "tour_class", "state",
                    "city", "category",
                    "status_colour", "stage_colour",)
    list_filter = ("tour_class",  "country", "state", "category",
                   "status", "stage")
    list_filter = ("status", "stage")
    search_fields = ("title", "agent__agent_uid", "tour_class", "state__name",
                     "city__name", "category__name")
    exclude = ('is_submitted',)
    readonly_fields = [field.name for field in Activity._meta.fields if field.name not in \
                       ['is_submitted', 'stage', 'id', 'updated_on', 'created_on']]
    inlines = [ActivityImageInline, 
               ActivityPricingInline, ActivityTourCategoryInline,
               ActivityCancellationPolicyInline, ActivityFaqQuestionAnswerInline
               ]

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
    list_display = ("truncated_title", "status_colour",)
    list_filter = ("status",)
    search_fields = ("title",)

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
    list_display = ("agent", "truncated_title", "tour_class", "state",
                    "city", "category",
                    "status_colour", "stage_colour",)
    list_filter = ("tour_class",  "country", "state", "category",
                   "status", "stage")
    list_filter = ("status", "stage")
    search_fields = ("title", "agent__agent_uid", "agent__first_name",
                     "state__name", "city__name", "category__name", "tour_class")
    readonly_fields = [field.name for field in Package._meta.fields if field.name not in \
                       ['is_submitted', 'stage', 'id', 'updated_on', 'created_on']]
    exclude = ('is_submitted',)

    inlines = [
        PackageImageInline,
        ItineraryInline, PricingInline, TourCategoryInline, 
        CancellationPolicyInline, PackageFaqQuestionAnswerInline,
        ]

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

class BookingAdmin(CustomModelAdmin):
    list_display = ("booking_id", "display_created_on", "tour_date", "user_uid","package_name","agent_id","booking_status_colour",)
    list_filter = ("booking_status",)
    search_fields = ("booking_id", "user__user_uid",)
    exclude = ("status",)

    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            return (
                (None, {
                    'fields': ('user','booking_id', 'package_uid', 'package_name', 
                               'agent_id','agent','order_id','booking_type','booking_amount','payment_id',
                               'booking_status','display_created_on','tour_date', 
                                'adult', 'child', 'infant', 'refund_amount',)
                }),
            )
        else:  # Add page
            return (
                (None, {
                    'fields': ('user', 'package', 
                               'adult', 'child', 'infant', 'booking_amount', 
                               'order_id', 'payment_id', 'booking_status','tour_date', 
                               'refund_amount', )
                }),
            )
    

    def agent(self, obj):
        return obj.package.agent.username if obj.package else None
    
    def agent_id(self, obj):
        return obj.package.agent.agent_uid if obj.package else None

    def user_uid(self, obj):
        return obj.user.user_uid if obj.user else None

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"

    def display_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
    display_created_on.short_description = "Booking date"

    def package_name(self, obj):
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"

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

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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
           
            return (
                (None, {
                    'fields': ('user', 'refund_uid','booking_uid', "booking_amount","booking_date",'package_name',
                               'package_uid', 'agent', 'agent_uid', 'display_created_on',
                                'refund_status', 'refund_amount','cancellation_policies')
                }),
            )
        else:  # Add page
            return (
                (None, {
                    'fields': ('package', 'booking', 'refund_status', 'refund_amount', 'user',)
                }),
            )
        
    list_display = ("refund_uid", "booking_uid", "user","package_name", "package_uid",
                     "agent", "agent_uid","refund_status_colour", "display_created_on",)
    
    list_filter = ("refund_status",)
    search_fields = ("refund_uid", "booking__booking_id", "package__title", "package__package_uid", 
                     "user__username")
    exclude = ('status',)

    def cancellation_policies(self, obj):
        if obj.package:
            policies = CancellationPolicy.objects.filter(package=obj.package)
            formatted_policies = ""
            for policy in policies:
                categories = policy.category.all()
                formatted_categories = []
                for category in categories:
                    if category.to_day == 0:
                        formatted_category = f"The cancellation policy before {category.from_day} days: {category.amount_percent}%"
                    else:
                        formatted_category = f"The cancellation policy from {category.from_day} to {category.to_day} days: {category.amount_percent}%"
                    formatted_categories.append(formatted_category)
                formatted_policies += "\n".join(formatted_categories) + "\n"
            return formatted_policies
        return None
    
    cancellation_policies.short_description = "Cancellation Policies"

    def agent(self, obj):
        return obj.package.agent.username if obj.package else None
    
    def agent_uid(self, obj):
        return obj.package.agent.agent_uid if obj.package else None

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"

    def package_name(self, obj):
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"
    

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
                                 'display_created_on', 'package_name','booking_amount','cancellation_policies','user')
        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):

        # Get the original object before saving changes
        original_obj = self.model.objects.get(pk=obj.pk) if change else None
        
        print(original_obj)
        # Save the changes
        super().save_model(request, obj, form, change)

        # Check if refund_status has changed and the new status is either "CANCELLED" or "REFUNDED"
        if change and obj.refund_status in ['CANCELLED', 'REFUNDED'] and obj.refund_status != original_obj.refund_status:
            print("hi2")
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
    agent.admin_order_field = 'Agent'  # Enable sorting by stage
    agent_uid.admin_order_field = 'Agent UID'  # Enable sorting by stage
    agent_uid.short_description = 'Agent UID'  # Set a custom column header
    display_created_on.admin_order_field = 'Transaction Date'  # Enable sorting by stage


class AgentTransactionSettlementAdmin(CustomModelAdmin):
    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            return (
                (None, {
                    'fields': ('agent_uid','transaction_id','booking_uid', "booking_amount","booking_type",
                                'package_name','package_uid',
                                'payment_settlement_status', 'payment_settlement_amount','payment_settlement_date')
                }),
            )
        else:  # Add page
            return (
                (None, {
                    'fields': ('package', 'booking', 'payment_settlement_status',
                                'payment_settlement_amount', 'agent','payment_settlement_date')
                }),
            )
        
    list_display = ("transaction_id", "booking_uid","booking_type", "package_uid", "agent_uid",
                    "payment_settlement_date", "payment_settlement_status_colour",)
    
    list_filter = ("payment_settlement_status","booking_type")
    search_fields = ("transaction_id", "booking__booking_id", "package__title", "package__package_uid", 
                     "agent__agent_uid", "agent__username")
    exclude = ('status',)

    def agent(self, obj):
        return obj.package.agent.username if obj.package else None
    
    
    def agent_uid(self, obj):
        return obj.package.agent.agent_uid if obj.package else None

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"

    def package_name(self, obj):
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"
    

    def booking_uid(self, obj):
        return obj.booking.booking_id if obj.booking else None
    booking_uid.short_description = "Booking UID"

    def booking_amount(self, obj):
        return obj.booking.booking_amount if obj.booking else None
    booking_amount.short_description = "Booking amount"

    def display_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
    display_created_on.short_description = "Transaction date"

    def has_add_permission(self, request, obj=None):
        return True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.readonly_fields += ('transaction_id', 'agent_uid', 'package_uid', 'booking_uid', 'agent',
                                 'display_created_on', 'package_name','booking_amount', 'booking_type')
        return super().change_view(request, object_id, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):

        # Get the original object before saving changes
        original_obj = self.model.objects.get(pk=obj.pk) if change else None
        
        print(original_obj)
        # Save the changes
        super().save_model(request, obj, form, change)

        if change and obj.payment_settlement_status in ['SUCCESSFUL'] and obj.payment_settlement_status != original_obj.payment_settlement_status:
            print("hi2")

            obj.transaction_id = f"EWTRAN-{obj.id}"
            obj.save()

    def payment_settlement_status_colour(self, obj):
        return refund_status_colour(obj.payment_settlement_status)

    payment_settlement_status_colour.short_description = 'Payment settlement status'  # Set a custom column header
    payment_settlement_status_colour.admin_order_field = 'Payment settlement status'  # Enable sorting by stage

    booking_uid.admin_order_field = 'Booking UID'  # Enable sorting by stage
    package_name.admin_order_field = 'Package Name'  # Enable sorting by stage
    package_uid.admin_order_field = 'Package UID'  # Enable sorting by stage
    agent_uid.admin_order_field = 'Agent UID'  # Enable sorting by stage
    agent_uid.short_description = 'Agent UID'  # Set a custom column header
    display_created_on.admin_order_field = 'Transaction Date'  # Enable sorting by stage

    def has_add_permission(self, request, obj=None):
        return False

class UserReviewAdmin(CustomModelAdmin):
    list_display = ("user", "package", "activity", "rating",)
    search_fields = ( "package__name", "user__username")
    list_filter = ("rating",)
    exclude = ('status', 'is_deleted', 'is_active')
    readonly_fields = ("user", "package", "activity", "rating", "review",
                       "booking", "agent", "agent_comment")
    fieldsets = (
        (None, {
            'fields': ("user", "package", "activity", "rating", "review",
                       "booking", "agent", "agent_comment",)
        }),
        )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


class AdvanceAmountPercentageSettingAdmin(CustomModelAdmin):
    list_display = ("id","percentage")
    search_fields = ( "id", "percentage")

class PackageCategoryAdmin(CustomModelAdmin):
    list_display = ("name",)
    search_fields = ( "name",)



def dashboard_page(request):

    total_user_count = User.objects.count()

    #Booking
    total_bookings_count = Booking.objects.count()
    successful_bookings = Booking.objects.filter(booking_status='SUCCESSFUL').count()
    failed_bookings = Booking.objects.filter(booking_status='FAILED').count()
    refunded_bookings = Booking.objects.filter(booking_status='REFUNDED').count()

    #Agents
    total_agent_count = Agent.objects.count()
    active_agents = Agent.objects.filter(stage='pending').count()
    inactive_agents = Agent.objects.filter(stage='approved').count()

    #Agent Transactions
    total_agent_transaction_count = AgentTransactionSettlement.objects.count()
    successful_agent_transaction_count = AgentTransactionSettlement.objects.filter(payment_settlement_status='SUCCESSFUL').count()
    failed_agent_transaction_count = AgentTransactionSettlement.objects.filter(payment_settlement_status='FAILED').count()
    pending_agent_transaction_count = AgentTransactionSettlement.objects.filter(payment_settlement_status='PENDING').count()

    #User Transactions
    total_user_transaction_count = UserRefundTransaction.objects.count()
    refunded_user_transaction_count = UserRefundTransaction.objects.filter(refund_status='REFUNDED').count()
    cancelled_user_transaction_count = UserRefundTransaction.objects.filter(refund_status='FAILED').count()
    pending_user_transaction_count = UserRefundTransaction.objects.filter(refund_status='CANCELLED').count()

  

    cards = {
        'total_bookings_count': total_bookings_count,
        'total_agent_count': total_agent_count,
        'total_user_count': total_user_count,
        'successful_bookings':successful_bookings,
        'failed_bookings':failed_bookings,
        'refunded_bookings':refunded_bookings,
        'active_agents':active_agents,
        'inactive_agents':inactive_agents,
        'total_agent_transaction_count':total_agent_transaction_count,
        'successful_agent_transaction_count':successful_agent_transaction_count,
        'failed_agent_transaction_count':failed_agent_transaction_count,
        'pending_agent_transaction_count':pending_agent_transaction_count,
        'total_user_transaction_count':total_user_transaction_count,
        'refunded_user_transaction_count':refunded_user_transaction_count,
        'cancelled_user_transaction_count':cancelled_user_transaction_count,
        'pending_user_transaction_count':pending_user_transaction_count
        
    }


    current_year = datetime.now().year

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

    print({
        'cards':cards,
        'barchart_booking':barchart_booking,})
    return render(request, 'admin/admin_dashboard.html', {
                                                'cards':cards,
                                                'barchart_booking':barchart_booking,})



def agent_bar_chart(request):

    total_agent_count = Agent.objects.count()
    active_agents = Agent.objects.filter(stage='approved').count()
    inactive_agents = Agent.objects.filter(stage='pending').count()

    labels = ['Total Agents', 'Active Agents', 'Inactive Agents']
    data = [total_agent_count, active_agents, inactive_agents]
    agent_data = {'labels': labels, 'data': data}

    return JsonResponse(agent_data)


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
admin.site.register(Currency)
admin.site.register(UserReview,UserReviewAdmin)

# admin.site.register(CancellationPolicy)
# admin.site.register(PackageCancellationCategory)

# admin.site.register(AdvanceAmountPercentageSetting,AdvanceAmountPercentageSettingAdmin)


admin.site.register(AgentTransactionSettlement,AgentTransactionSettlementAdmin)
admin.site.register(UserRefundTransaction,UserRefundTransactionAdmin)
