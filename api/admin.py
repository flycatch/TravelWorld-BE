from django.contrib import admin
from django.contrib.auth.models import Group

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.models import TokenProxy

from api import models as api_models


admin.site.site_header = 'Explore World'

class CustomStatusFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return [
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        elif self.value() == 'inactive':
            return queryset.filter(is_active=False)


class AgentAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('username', 'first_name', 'last_name', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'stage')}),
        ('Activity History', {'fields': ('date_joined', 'last_login')}),
    )
    
    list_display = ("username", "first_name", "last_name", "email", "phone", "is_active", "stage")
    list_filter = (CustomStatusFilter, "stage")
    list_editable = ("is_active", "stage",)
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    # def has_add_permission(self, request):
    #     return False


class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('username', 'first_name', 'last_name', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'user_permissions',)}),
        ('Activity History', {'fields': ('date_joined', 'last_login')}),
        # Add your custom fieldsets here
    )
    
    list_display = ("username", "first_name", "last_name", "email", "phone", "is_active")
    list_filter = (CustomStatusFilter,)
    list_editable = ("is_active",)
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    def has_add_permission(self, request):
        return False
    

class CountryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "country")


class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state")


class InclusionsAdmin(admin.ModelAdmin):
    list_display = ("name", "stage",)
    list_filter = ("stage",)
    list_editable = ("stage",)
    search_fields = ("name",)


class ExclusionsAdmin(admin.ModelAdmin):
    list_display = ("name", "stage")
    list_filter = ("stage",)
    list_editable = ("stage",)
    search_fields = ("name",)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "package", "get_agent", "is_active", "stage")
    list_editable = ("is_active", "stage",)
    list_filter = (CustomStatusFilter, "stage",)
    search_fields = ("name", "package__agent__username")

    def get_agent(self, obj):
        return obj.package.agent
    
    get_agent.short_description = "Agent"  # Set a custom column header
    get_agent.admin_order_field = 'package__agent__username'  # Set the ordering field for the column


class AttractionImageInline(admin.TabularInline):
    model = api_models.AttractionImage
    extra = 1


class PackageImageInline(admin.TabularInline):
    model = api_models.PackageImage
    extra = 2


class AttractionAdmin(admin.ModelAdmin):
    list_display = ("title", "overview", "is_active",)
    list_filter = (CustomStatusFilter,)
    list_editable = ("is_active",)
    search_fields = ("title",)

    inlines = [AttractionImageInline]


class PackageAdmin(admin.ModelAdmin):
    list_display = ("agent", "title", "tour_type", "country", "state",
                    "city", "category", "duration_day",
                    "pickup_point", "pickup_time", "drop_point",
                    "drop_time", "is_active", "stage")
    list_filter = ("tour_type",  "country", "state", "category",
                   "is_active", "stage")
    list_filter = (CustomStatusFilter, "stage")
    search_fields = ("title", "agent", "country", "state")
    list_editable = ("is_active", "stage",)

    inlines = [PackageImageInline]

    # def has_add_permission(self, request):
    #     return False



# Unregister model
# admin.site.unregister(Token)
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

admin.site.register(api_models.TourType)
admin.site.register(api_models.PackageCategory)
