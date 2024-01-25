from django.contrib import admin
from api import models as api_models
# Register your models here.


class AgentAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "first_name", "last_name", "email", "phone", "is_approved", "is_rejected")
    # list_filter = ("type", "status")
    list_editable = ("is_approved", "is_rejected")


class CountryAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)


class StateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country")


class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "state")


class InclusionsAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)


class ExclusionsAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "package", "name", "is_published", "is_rejected")


class AttractionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "overview", "is_published", "created_by")


admin.site.register(api_models.User)
admin.site.register(api_models.Agent, AgentAdmin)
admin.site.register(api_models.Country, CountryAdmin)
admin.site.register(api_models.City, CityAdmin)
admin.site.register(api_models.State, StateAdmin)
admin.site.register(api_models.Inclusions, InclusionsAdmin)
admin.site.register(api_models.Exclusions, ExclusionsAdmin)
admin.site.register(api_models.Activity, ActivityAdmin)
admin.site.register(api_models.Attraction, AttractionAdmin)
