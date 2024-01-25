from django.contrib import admin
from api.models import Agent, User, City
# Register your models here.


class AgentAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "phone", "is_approved", "is_rejected")
    # list_filter = ("type", "status")
    list_editable = ("is_approved", "is_rejected")

admin.site.register(User)
admin.site.register(Agent, AgentAdmin)
admin.site.register(City)
