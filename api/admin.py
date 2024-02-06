from django.contrib import admin
from django.contrib.auth.models import Group
from django.template.defaultfilters import truncatewords

from rest_framework.authtoken.models import TokenProxy

from api.models import *
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
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    def has_add_permission(self, request):
        return False


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
    list_display = ("name", "stage", "status")
    list_filter = ("stage", "status")
    search_fields = ("name",)


class ExclusionsAdmin(CustomModelAdmin):
    list_display = ("name", "stage", "status")
    list_filter = ("stage", "status")
    search_fields = ("name",)


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
    list_display = ("name", "description", "city", "agent", "status", "stage",)
    list_filter = ("status", "stage",)
    search_fields = ("name", "agent__username", "city__name",)

    inlines = [ActivityImageInline]

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
    list_display = ("agent", "title", "tour_type", "state",
                    "city", "category", "duration_day",
                    "status", "stage")
    list_filter = ("tour_type",  "country", "state", "category",
                   "status", "stage")
    list_filter = ("status", "stage")
    search_fields = ("title", "agent", "country", "state")

    inlines = [PackageImageInline]

    # def has_add_permission(self, request):
    #     return False


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

# admin.site.register(api_models.TourType)
admin.site.register(PackageCategory)
