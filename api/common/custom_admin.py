from django.utils.html import strip_tags
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from api.models import (Itinerary, Pricing, UserReviewImage,
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
    verbose_name = 'Image'
    verbose_name_plural = 'Images'


class PackageImageInline(CustomTabularImageInline):
    model = PackageImage
    verbose_name = 'Image'
    verbose_name_plural = 'Images'


class AttractionImageInline(admin.TabularInline):
    model = AttractionImage
    extra = 3
    verbose_name = 'Image'
    verbose_name_plural = 'Images'


class ItineraryInline(CustomStackedInline):
    model = Itinerary
    exclude = ['overview', 'description', 'status']

    def overview_display(self, instance):
        """Custom method to display overview without HTML tags"""
        return strip_tags(instance.overview)
    overview_display.short_description = 'Overview'

    def description_display(self, instance):
        """Custom method to display description without HTML tags"""
        return strip_tags(instance.description)
    description_display.short_description = 'Description'

    readonly_fields = ('overview_display', 'description_display', 'important_message')


class PackageInformationsInline(CustomStackedInline):
    model = PackageInformations
    exclude = ['exclusiondetails', 'status']
    verbose_name = 'Information'
    verbose_name_plural = 'Information'

class PricingInline(CustomStackedInline):
    model = Pricing
    exclude = ['activity','status']
    verbose_name = 'Pricing'
    verbose_name_plural = 'Pricing'

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    

class TourCategoryInline(CustomStackedInline):
    model = TourCategory
    verbose_name = 'Tour Category'
    verbose_name_plural = 'Tour Category'


class CancellationPolicyInline(CustomStackedInline):
    model = CancellationPolicy
    template = 'admin/inline_admin.html'


class PackageFaqQuestionAnswerInline(CustomStackedInline):
    model = PackageFaqQuestionAnswer
    template = 'admin/inline_admin.html'
    verbose_name = 'Faq'
    verbose_name_plural = 'Faq'

class ActivityItineraryInline(CustomStackedInline):
    model = ActivityItinerary
    verbose_name = 'Itinerary'
    verbose_name_plural = 'Itinerary'
    exclude = ['overview', 'description', 'status']

    def overview_display(self, instance):
        """Custom method to display overview without HTML tags"""
        return strip_tags(instance.overview)
    overview_display.short_description = 'Overview'

    def description_display(self, instance):
        """Custom method to display description without HTML tags"""
        return strip_tags(instance.description)
    description_display.short_description = 'Description'

    readonly_fields = ('overview_display', 'description_display', 'important_message')


class ActivityInformationsInline(CustomStackedInline):
    model = ActivityInformations
    exclude = ['exclusiondetails', 'status']
    verbose_name = 'Information'
    verbose_name_plural = 'Information'

class ActivityPricingInline(CustomStackedInline):
    model = Pricing
    exclude = ['package','status']

    def has_change_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    verbose_name = 'Pricing'
    verbose_name_plural = 'Pricing'


class ActivityTourCategoryInline(CustomStackedInline):
    model = ActivityTourCategory
    verbose_name = 'Tour Category'
    verbose_name_plural = 'Tour Category'


class ActivityFaqQuestionAnswerInline(CustomStackedInline):
    model = ActivityFaqQuestionAnswer
    template = 'admin/inline_admin.html'
    verbose_name = 'Faq'
    verbose_name_plural = 'Faq'


class ActivityCancellationPolicyInline(CustomStackedInline):
    model = ActivityCancellationPolicy
    template = 'admin/inline_admin.html'
    verbose_name = 'Cancellation Policy'
    verbose_name_plural = 'Cancellation Policies'


class UserReviewImageInline(admin.TabularInline):
    model = UserReviewImage
    readonly_fields = ('images',)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    verbose_name = 'Images'
    verbose_name_plural = 'Images'
