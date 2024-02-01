from django.contrib import admin


admin.site.site_header = 'Explore World'


class CustomModelAdmin(admin.ModelAdmin):
    list_per_page = 10

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)