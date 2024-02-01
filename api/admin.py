from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.defaultfilters import truncatewords

from rest_framework.authtoken.models import TokenProxy

from api import models as api_models
from api.common.custom_admin import CustomModelAdmin


class AgentAdmin(CustomModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('username', 'first_name',
         'last_name', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('status', 'stage')}),
        ('Activity History', {'fields': ('date_joined', 'last_login')}),
    )

    list_display = ("username", "first_name", "last_name", "email", "phone", "status", "stage")
    list_filter = ("status", "stage")
    list_editable = ("status", "stage",)
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    def has_add_permission(self, request):
        return False


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
    list_editable = ("status",)
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    def has_add_permission(self, request):
        return False


class CountryAdmin(CustomModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    exclude = ("status",)


class StateAdmin(CustomModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)
    exclude = ("status",)


class CityAdmin(CustomModelAdmin):
    list_display = ("name", "state")
    search_fields = ("name",)
    exclude = ("status",)


class InclusionsAdmin(CustomModelAdmin):
    list_display = ("name", "stage",)
    list_filter = ("stage",)
    list_editable = ("stage",)
    search_fields = ("name",)


class ExclusionsAdmin(CustomModelAdmin):
    list_display = ("name", "stage")
    list_filter = ("stage",)
    list_editable = ("stage",)
    search_fields = ("name",)


class ActivityAdmin(CustomModelAdmin):
    list_display = ("name", "package", "get_agent", "status", "stage")
    list_editable = ("status", "stage",)
    list_filter = ("status", "stage",)
    search_fields = ("name", "package__agent__username")

    def get_agent(self, obj):
        return obj.package.agent

    def has_add_permission(self, request):
        return False

    get_agent.short_description = "Agent"  # Set a custom column header
    get_agent.admin_order_field = 'package__agent__username'  # Set the ordering field for the column


class AttractionImageInline(admin.TabularInline):
    model = api_models.AttractionImage
    extra = 3


class PackageImageInline(admin.TabularInline):
    model = api_models.PackageImage
    extra = 3


class AttractionAdmin(CustomModelAdmin):
    list_display = ("title", "truncated_overview", "status",)
    list_filter = ("status",)
    list_editable = ("status",)
    search_fields = ("title",)

    inlines = [AttractionImageInline]

    def truncated_overview(self, obj):
        # Display truncated overview in the admin list view
        return truncatewords(obj.overview, 80)

    truncated_overview.short_description = 'Overview'


class PackageAdmin(CustomModelAdmin):
    list_display = ("agent", "title", "tour_type", "country", "state",
                    "city", "category", "duration_day",
                    "pickup_point", "pickup_time", "drop_point",
                    "drop_time", "status", "stage")
    list_filter = ("tour_type",  "country", "state", "category",
                   "status", "stage")
    list_filter = ("status", "stage")
    search_fields = ("title", "agent", "country", "state")
    list_editable = ("status", "stage",)

    inlines = [PackageImageInline]

    def has_add_permission(self, request):
        return False


# Unregister model
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)

admin.site.register(api_models.User, UserAdmin)
admin.site.register(api_models.Agent, AgentAdmin)

admin.site.register(api_models.Package, PackageAdmin)
admin.site.register(api_models.Activity, ActivityAdmin)
admin.site.register(api_models.Attraction, AttractionAdmin)
admin.site.register(api_models.Inclusions, InclusionsAdmin)
admin.site.register(api_models.Exclusions, ExclusionsAdmin)

admin.site.register(api_models.Country, CountryAdmin)
admin.site.register(api_models.State, StateAdmin)
admin.site.register(api_models.City, CityAdmin)

# admin.site.register(api_models.TourType)
# admin.site.register(api_models.PackageCategory)
