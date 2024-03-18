from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from api.models import (Itinerary, Pricing, ActivityPricing,
                        TourCategory, ActivityTourCategory,
                        PackageFaqQuestionAnswer, ActivityFaqQuestionAnswer,
                        CancellationPolicy, ActivityCancellationPolicy,
                        PackageImage, ActivityImage, AttractionImage,
                        PackageInformations,ActivityItinerary, ActivityInformations)


admin.site.site_header = 'Explore World'


class CustomModelAdmin(admin.ModelAdmin):
    list_per_page = 10

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)

        if hasattr(formfield, 'widget') and isinstance(formfield.widget, RelatedFieldWidgetWrapper):
            formfield.widget.can_view_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_add_related = False

        return formfield


class CustomStackedInline(admin.StackedInline):
    extra = 0
    exclude = ('status',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CustomTabularImageInline(admin.TabularInline):
    extra = 0
    exclude = ("status",)
    readonly_fields = ('image',)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class ActivityImageInline(CustomTabularImageInline):
    model = ActivityImage


class PackageImageInline(CustomTabularImageInline):
    model = PackageImage


class AttractionImageInline(admin.TabularInline):
    model = AttractionImage
    extra = 3


class ItineraryInline(CustomStackedInline):
    model = Itinerary


class PackageInformationsInline(CustomStackedInline):
    model = PackageInformations


class PricingInline(admin.TabularInline):
    model = Pricing
    exclude = ['activity','status']

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    


class TourCategoryInline(CustomStackedInline):
    model = TourCategory


class CancellationPolicyInline(CustomStackedInline):
    model = CancellationPolicy
    template = 'admin/inline_admin.html'


class PackageFaqQuestionAnswerInline(CustomStackedInline):
    model = PackageFaqQuestionAnswer
    template = 'admin/inline_admin.html'

class ActivityItineraryInline(CustomStackedInline):
    model = ActivityItinerary


class ActivityInformationsInline(CustomStackedInline):
    model = ActivityInformations


class ActivityPricingInline(CustomStackedInline):
    model = Pricing
    exclude = ['package','status']

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class ActivityTourCategoryInline(CustomStackedInline):
    model = ActivityTourCategory


class ActivityFaqQuestionAnswerInline(CustomStackedInline):
    model = ActivityFaqQuestionAnswer
    template = 'admin/inline_admin.html'


class ActivityCancellationPolicyInline(CustomStackedInline):
    model = ActivityCancellationPolicy
    template = 'admin/inline_admin.html'

