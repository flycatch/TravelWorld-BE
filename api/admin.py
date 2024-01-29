from django.contrib import admin
from api import models as api_models
# Register your models here.


class AgentAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Profile Details', {'fields': ('username', 'first_name', 'last_name', 'phone', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_approved', 'is_rejected', 'user_permissions')}),
        ('Activity History', {'fields': ('date_joined', 'last_login')}),
        # Add your custom fieldsets here
    )
    
    list_display = ("id", "username", "first_name", "last_name", "email", "phone", "is_approved", "is_rejected")
    # list_filter = ("type", "status")
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
    list_filter = ("name", "is_approved", "is_rejected",)
    list_editable = ("is_approved", "is_rejected")
    search_fields = ("name",)


class ExclusionsAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_approved", "is_rejected")
    list_filter = ("name", "is_approved", "is_rejected",)
    list_editable = ("is_approved", "is_rejected")
    search_fields = ("name",)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "package", "name", "is_published", "is_rejected")


class AttractionImageInline(admin.TabularInline):
    model = api_models.AttractionImage
    extra = 1


class AttractionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "overview", "is_published",)
    list_filter = ("title", "is_published",)
    list_editable = ("is_published",)
    search_fields = ("title",)

    inlines = [AttractionImageInline]

admin.site.register(api_models.User, UserAdmin)
admin.site.register(api_models.Agent, AgentAdmin)
admin.site.register(api_models.Country, CountryAdmin)
admin.site.register(api_models.City, CityAdmin)
admin.site.register(api_models.State, StateAdmin)
admin.site.register(api_models.Inclusions, InclusionsAdmin)
admin.site.register(api_models.Exclusions, ExclusionsAdmin)
admin.site.register(api_models.Activity, ActivityAdmin)
admin.site.register(api_models.Attraction, AttractionAdmin)
