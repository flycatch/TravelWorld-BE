from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from api.models import (Itinerary, Pricing, ActivityPricing,
                        TourCategory, ActivityTourCategory,
                        PackageFaqQuestionAnswer, ActivityFaqQuestionAnswer,
                        CancellationPolicy, ActivityCancellationPolicy,
                        PackageImage, ActivityImage, AttractionImage)


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


class ActivityImageInline(admin.TabularInline):
    model = ActivityImage
    extra = 0
    exclude = ("status",)
    readonly_fields = ('image',)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 0
    exclude = ("status",)
    readonly_fields = ('image',)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class AttractionImageInline(admin.TabularInline):
    model = AttractionImage
    extra = 3


class ItineraryInline(admin.StackedInline):  # or StackedInline
    model = Itinerary
    extra = 0

class PricingInline(admin.StackedInline):
    model = Pricing
    extra = 0
    exclude = ("status",)

class TourCategoryInline(admin.StackedInline):
    model = TourCategory
    extra = 0
    exclude = ("status",)

class CancellationPolicyInline(admin.StackedInline):
    model = CancellationPolicy
    extra = 0
    exclude = ("status",)

class PackageFaqQuestionAnswerInline(admin.StackedInline):
    model = PackageFaqQuestionAnswer
    extra = 0
    exclude = ("status",)


class ActivityPricingInline(admin.StackedInline):
    model = ActivityPricing
    extra = 0
    exclude = ("status",)

class ActivityTourCategoryInline(admin.StackedInline):
    model = ActivityTourCategory
    extra = 0
    exclude = ("status",)

class ActivityFaqQuestionAnswerInline(admin.StackedInline):
    model = ActivityFaqQuestionAnswer
    extra = 0
    exclude = ("status",)

class ActivityCancellationPolicyInline(admin.StackedInline):
    model = ActivityCancellationPolicy
    extra = 0
    exclude = ("status",)
