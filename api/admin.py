from decimal import Decimal

from api.common.custom_admin import CustomModelAdmin
from api.models import *
from api.tasks import *
from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.defaultfilters import truncatewords
from django.utils.html import format_html
from rest_framework.authtoken.models import TokenProxy


class AgentAdmin(CustomModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('agent_uid', 'username', 'first_name',
         'last_name', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('status', 'stage')}),
        ('Activity History', {'fields': ('date_joined', 'last_login')}),
    )

    list_display = ("id","agent_uid", "username", "first_name", "last_name", "email", "phone", "status", "stage_colour")
    list_filter = ("status", "stage")
    search_fields = ("username", "first_name", "last_name", "email", "phone")
    readonly_fields = ("agent_uid",)

    def stage_colour(self, obj):
        if obj.stage == 'approved':
            color = 'green'
        elif obj.stage == 'rejected':
            color = 'red'
        else:
            color = 'black'  # Default color

        return format_html('<span style="color: {};">{}</span>', color, obj.stage)

    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage

    # def has_add_permission(self, request):
    #     return False


class UserAdmin(CustomModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('username', 'first_name',
         'last_name', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('status', 'user_permissions',)}),
        ('Activity History', {'fields': ('date_joined', 'last_login')}),
        # Add your custom fieldsets here
    )

    list_display = ("username", "first_name", "last_name", "email", "phone", "status")
    list_filter = ("status",)
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    # def has_add_permission(self, request):
    #     return False


class CountryAdmin(CustomModelAdmin):
    list_display = ("name", "image")
    search_fields = ("name",)
    exclude = ("status",)


class StateAdmin(CustomModelAdmin):
    list_display = ("name", "country", "image")
    search_fields = ("name", "country__name")
    exclude = ("status",)


class CityAdmin(CustomModelAdmin):
    list_display = ("name", "state", "image")
    search_fields = ("name", "state__name")
    exclude = ("status",)


class InclusionsAdmin(CustomModelAdmin):
    list_display = ("name", "stage_colour", "status")
    list_filter = ("stage", "status")
    search_fields = ("name",)

    def stage_colour(self, obj):
        if obj.stage == 'approved':
            color = 'green'
        elif obj.stage == 'rejected':
            color = 'red'
        else:
            color = 'black'  # Default color

        return format_html('<span style="color: {};">{}</span>', color, obj.stage)

    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage


class ExclusionsAdmin(CustomModelAdmin):
    list_display = ("name", "stage_colour", "status")
    list_filter = ("stage", "status")
    search_fields = ("name",)

    def stage_colour(self, obj):
        if obj.stage == 'approved':
            color = 'green'
        elif obj.stage == 'rejected':
            color = 'red'
        else:
            color = 'black'  # Default color

        return format_html('<span style="color: {};">{}</span>', color, obj.stage)

    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage

class ActivityImageInline(admin.TabularInline):
    model = ActivityImage
    extra = 3


class AttractionImageInline(admin.TabularInline):
    model = AttractionImage
    extra = 3


class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 3


class ActivityAdmin(CustomModelAdmin):
    list_display = ("id","agent", "title", "tour_class", "state",
                    "city", "category",
                    "status", "stage_colour",)
    list_filter = ("tour_class",  "country", "state", "category",
                   "status", "stage")
    list_filter = ("status", "stage")
    search_fields = ("title", "agent__first_name", "country__name", "state__name")

    inlines = [ActivityImageInline]

    def stage_colour(self, obj):
        if obj.stage == 'approved':
            color = 'green'
        elif obj.stage == 'rejected':
            color = 'red'
        else:
            color = 'black'  # Default color

        return format_html('<span style="color: {};">{}</span>', color, obj.stage)

    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage


class AttractionAdmin(CustomModelAdmin):
    list_display = ("title", "truncated_overview", "status",)
    list_filter = ("status",)
    search_fields = ("title",)

    inlines = [AttractionImageInline]

    def truncated_overview(self, obj):
        # Display truncated overview in the admin list view
        return truncatewords(obj.overview, 80)

    truncated_overview.short_description = 'Overview'


class PackageAdmin(CustomModelAdmin):
    list_display = ("id","agent", "title", "tour_class", "state",
                    "city", "category",
                    "status", "stage_colour",)
    list_filter = ("tour_class",  "country", "state", "category",
                   "status", "stage")
    list_filter = ("status", "stage")
    search_fields = ("title", "agent__first_name", "country__name", "state__name")

    inlines = [PackageImageInline]

    def stage_colour(self, obj):
        if obj.stage == 'approved':
            color = 'green'
        elif obj.stage == 'rejected':
            color = 'red'
        else:
            color = 'black'  # Default color

        return format_html('<span style="color: {};">{}</span>', color, obj.stage)

    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage

    # def has_add_permission(self, request):
    #     return False


class BookingAdmin(CustomModelAdmin):
    list_display = ("id","booking_id","user","package_name","agent","agent_id","booking_status","tour_date", "display_created_on")
    list_filter = ("booking_status",)
    search_fields = ("booking_status","booking_id","user")
    exclude = ("status",)

    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            return (
                (None, {
                    'fields': ('user','booking_id', 'package_uid', 'package_name', 
                               'agent_id','agent','order_id','booking_amount','payment_id',
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

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"

    def display_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
    display_created_on.short_description = "Booking date"

    def package_name(self, obj):
        return obj.package.title if obj.package else None
    package_name.short_description = "Package Name"

    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     self.readonly_fields += ('display_created_on', 'package_name')
    #     return super().change_view(request, object_id, form_url, extra_context)

    agent.admin_order_field = 'package__agent__username' 
    agent_id.admin_order_field = 'package__agent__agent_uid'  
    display_created_on.admin_order_field = 'created_on'  # Enable sorting by created_on

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
                     "agent", "agent_uid","refund_status", "display_created_on",)
    
    list_filter = ("refund_status",)
    search_fields = ("refund_status","refund_uid","user")
    exclude = ('status',)


    def cancellation_policies(self, obj):
        if obj.package:
            policies = CancellationPolicy.objects.filter(package=obj.package)
            formatted_policies = "\n".join([f"The cancellation policy from {policy.from_day} to {policy.to_day} days : {policy.amount_percent} %" for policy in policies])
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
        return obj.package.title if obj.package else None
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
    display_created_on.short_description = "Transaction date"

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


class AgentTransactionSettlementAdmin(CustomModelAdmin):
    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            return (
                (None, {
                    'fields': ('agent_uid','transaction_id','booking_uid', "booking_amount", 'package_name',
                               'package_uid',
                                'payment_settlement_status', 'payment_settlement_amount','payment_settlement_date')
                }),
            )
        else:  # Add page
            return (
                (None, {
                    'fields': ('package', 'booking', 'payment_settlement_status', 'payment_settlement_amount', 'agent','payment_settlement_date')
                }),
            )
        
    list_display = ("transaction_id", "booking_uid","package_name", "package_uid",
                     "agent", "agent_uid","payment_settlement_status", "payment_settlement_date",)
    
    list_filter = ("payment_settlement_status",)
    search_fields = ("payment_settlement_status","transaction_id","user")
    exclude = ('status',)

    def agent(self, obj):
        return obj.package.agent.username if obj.package else None
    
    
    def agent_uid(self, obj):
        return obj.package.agent.agent_uid if obj.package else None

    def package_uid(self, obj):
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"

    def package_name(self, obj):
        return obj.package.title if obj.package else None
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
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.readonly_fields += ('transaction_id', 'agent_uid', 'package_uid', 'booking_uid', 'agent',
                                 'display_created_on', 'package_name','booking_amount')
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


class UserReviewAdmin(CustomModelAdmin):
    list_display = ("id","user", "package", "rating", "review", "is_active", "is_deleted")
    search_fields = ( "package__name", "user__username")
    exclude = ('status',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


           
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

admin.site.register(PackageCategory)
admin.site.register(Currency)
admin.site.register(UserReview,UserReviewAdmin)
# admin.site.register(CancellationPolicy)

admin.site.register(AgentTransactionSettlement,AgentTransactionSettlementAdmin)
admin.site.register(UserRefundTransaction,UserRefundTransactionAdmin)
