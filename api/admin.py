from django.contrib import admin
from api import models as api_models
# Register your models here.


class AgentAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('username', 'first_name', 'last_name', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_approved', 'is_rejected', 'user_permissions')}),
        ('Activity History', {'fields': ('date_joined', 'last_login')}),
    )
    
    list_display = ("id", "username", "first_name", "last_name", "email", "phone", "is_approved", "is_rejected")
    list_filter = ("is_approved", "is_rejected", "is_active")
    list_editable = ("is_approved", "is_rejected")
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    def has_add_permission(self, request):
        return False

class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('username', 'first_name', 'last_name', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'user_permissions',)}),
        ('Activity History', {'fields': ('date_joined', 'last_login')}),
        # Add your custom fieldsets here
    )
    
    list_display = ("id", "username", "first_name", "last_name", "email", "phone", "is_active")
    list_filter = ("is_active",)
    list_editable = ("is_active",)
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    def has_add_permission(self, request):
        return False
    

class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)
    search_fields = ("name",)


class StateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country")


class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "state")


class InclusionsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_approved", "is_rejected",)
    list_filter = ("is_approved", "is_rejected",)
    list_editable = ("is_approved", "is_rejected")
    search_fields = ("name",)


class ExclusionsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_approved", "is_rejected")
    list_filter = ("is_approved", "is_rejected",)
    list_editable = ("is_approved", "is_rejected")
    search_fields = ("name",)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "package", "agent_name", "is_active", "is_approved", "is_rejected",)
    list_editable = ("is_active", "is_approved", "is_rejected")
    list_filter = ("is_active", "is_approved", "is_rejected",)
    search_fields = ("name", "package__agent__username")

    def agent_name(self, obj):
        return obj.package.agent


class AttractionImageInline(admin.TabularInline):
    model = api_models.AttractionImage
    extra = 1


class PackageImageInline(admin.TabularInline):
    model = api_models.PackageImage
    extra = 2


class AttractionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "overview", "is_published",)
    list_filter = ("is_published",)
    list_editable = ("is_published",)
    search_fields = ("title",)

    inlines = [AttractionImageInline]


class PackageAdmin(admin.ModelAdmin):
    list_display = ("id", "agent", "title", "tour_type", "country", "state",
                    "city", "category", "min_members", "max_members", "duration_day",
                    "duration_hour", "pickup_point", "pickup_time", "drop_point",
                    "drop_time", "is_published", "is_approved", "is_rejected")
    list_filter = ("tour_type",  "country", "state", "category",
                   "is_published", "is_approved", "is_rejected")
    list_editable = ("is_published", "is_approved", "is_rejected")
    search_fields = ("title", "agent", "country", "state")

    inlines = [PackageImageInline]

    # def has_add_permission(self, request):
    #     return False
    

admin.site.register(api_models.User, UserAdmin)
admin.site.register(api_models.Agent, AgentAdmin)
admin.site.register(api_models.Country, CountryAdmin)
admin.site.register(api_models.City, CityAdmin)
admin.site.register(api_models.State, StateAdmin)
admin.site.register(api_models.Inclusions, InclusionsAdmin)
admin.site.register(api_models.Exclusions, ExclusionsAdmin)
admin.site.register(api_models.Activity, ActivityAdmin)
admin.site.register(api_models.Attraction, AttractionAdmin)
admin.site.register(api_models.Package, PackageAdmin)

admin.site.register(api_models.TourType)
admin.site.register(api_models.PackageCategory)
