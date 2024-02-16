from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.defaultfilters import truncatewords

from rest_framework.authtoken.models import TokenProxy

from api.models import *
from api.common.custom_admin import CustomModelAdmin
from django.utils.html import format_html
from api.tasks import *


class AgentAdmin(CustomModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('agent_uid', 'username', 'first_name',
         'last_name', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('status', 'stage')}),
        ('Activity History', {'fields': ('date_joined', 'last_login')}),
    )

    list_display = ("agent_uid", "username", "first_name", "last_name", "email", "phone", "status", "stage_colour")
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
    list_display = ("name", "description", "city", "agent", "status", "stage_colour",)
    list_filter = ("status", "stage",)
    search_fields = ("name", "agent__username", "city__name",)

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

    # def has_add_permission(self, request):
    #     return False


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
    list_display = ("agent", "title", "tour_class", "state",
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
    list_display = ("booking_id","user","package_name","agent","agent_id","booking_status","check_in", "display_created_on")
    list_filter = ("booking_status",)
    search_fields = ("booking_status","booking_id","user")
    exclude = ("status",)

    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            return (
                (None, {
                    'fields': ('booking_id','user', 'package_uid', 'package_name', 
                               'agent','agent_id','adult', 'child', 'infant', 'amount', 
                               'order_id', 'payment_id', 'booking_status','check_in', 
                               'display_created_on', 'refund_amount', 'is_paid',)
                }),
            )
        else:  # Add page
            return (
                (None, {
                    'fields': ('user', 'package', 
                               'adult', 'child', 'infant', 'amount', 
                               'order_id', 'payment_id', 'booking_status','check_in', 
                               'refund_amount', 'is_paid',)
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


class TransactionAdmin(CustomModelAdmin):
    def get_fieldsets(self, request, obj=None):
        if obj:  # Detail page
            return (
                (None, {
                    'fields': ('transaction_uid','booking_uid', 'user', 'package_name',
                               'package_uid', 'agent', 'agent_uid', 'display_created_on',
                                'refund_status', 'refund_amount',)
                }),
            )
        else:  # Add page
            return (
                (None, {
                    'fields': ('package', 'booking', 'refund_status', 'refund_amount', 'user',)
                }),
            )
        
    list_display = ("transaction_uid", "booking_uid", "user","package_name", "package_uid",
                     "agent", "agent_uid","refund_status", "display_created_on",)
    list_filter = ("refund_status",)
    search_fields = ("refund_status","transaction_uid","user")
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

    def display_created_on(self, obj):
        return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
    display_created_on.short_description = "Transaction date"

    def has_add_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.readonly_fields += ('transaction_uid', 'agent_uid', 'package_uid', 'booking_uid', 'agent',
                                 'display_created_on', 'package_name')
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
admin.site.register(Transaction,TransactionAdmin)

admin.site.register(PackageCategory)
