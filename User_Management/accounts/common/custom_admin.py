"""
Admin module for managing models in the API app.

This module contains custom ModelAdmin classes and inline classes for managing various models
within the API app in the Django admin interface. It includes configurations for displaying
and managing models such as Itinerary, Pricing, UserReviewImage, AgentBankDetails,
PackageFaqQuestionAnswer, ActivityFaqQuestionAnswer, CancellationPolicy, ActivityCancellationPolicy,
Informations, PackageImage, ActivityImage, AttractionImage, InclusionExclusion, ActivityItinerary,
ActivityInformations, and BlogImage.

Classes:
- CustomJSONEncoder: Custom JSON encoder class for handling Promise objects.
- CustomModelAdmin: Base class for customizing ModelAdmin behavior.
- CustomStackedInline: Custom inline class based on admin.StackedInline.
- CustomTabularImageInline: Custom inline class for managing image models
    based on admin.TabularInline.
- ActivityImageInline: Inline class for managing ActivityImage models within related models.
- PackageImageInline: Inline class for managing PackageImage models within related models.
- AttractionImageInline: Inline class for managing AttractionImage models within related models.
- ItineraryInline: Inline class for managing Itinerary models within related models.
- InclusionExclusionInline: Inline class for managing InclusionExclusion models
    within related models.
- InformationsInline: Inline class for managing Informations models within related models.
- PricingInline: Inline class for managing Pricing models within related models.
- CancellationPolicyInline: Inline class for managing CancellationPolicy models
    within related models.
- PackageFaqQuestionAnswerInline: Inline class for managing PackageFaqQuestionAnswer models
    within related models.
- ActivityItineraryInline: Inline class for managing ActivityItinerary models within related models.
- ActivityInformationsInline: Inline class for managing ActivityInformations models
    within related models.
- ActivityPricingInline: Inline class for managing ActivityPricing models within related models.
- ActivityFaqQuestionAnswerInline: Inline class for managing ActivityFaqQuestionAnswer models
    within related models.
- ActivityCancellationPolicyInline: Inline class for managing ActivityCancellationPolicy models
    within related models.
- UserReviewImageInline: Inline class for managing UserReviewImage models within related models.
- BlogImageInline: Inline class for managing BlogImage models within related models.
- AgentBankDetailsInline: Inline class for managing AgentBankDetails models within related models.
"""

import json
from datetime import datetime

from django.contrib import admin
from django.utils.functional import Promise
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from api.models import (Itinerary, Pricing, UserReviewImage, AgentBankDetails,
                        PackageFaqQuestionAnswer, ActivityFaqQuestionAnswer,
                        CancellationPolicy, ActivityCancellationPolicy, Informations,
                        PackageImage, ActivityImage, AttractionImage, InclusionExclusion,
                        ActivityItinerary, ActivityInformations, BlogImage)
from api.signals import log_change, get_changes


admin.site.site_header = 'Explore World'


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder class.

    This class overrides the default method to handle Promise objects
    during JSON serialization.
    """
    # This is a custom JSON encoder class that overrides the default method.
    def default(self, obj):
        """
        Override default method for JSON serialization.

        This method is called for each object in the JSON data. It checks if the
        object is a Promise (a type of asynchronous operation). If it is a Promise,
        it converts it to a string using the force_str function. If it is not a
        Promise, it calls the default method of the parent class.
        """

        # This method is called for each object in the JSON data. It checks if the
        # object is a Promise (a type of asynchronous operation).
        if isinstance(obj, Promise):
            # If it is a Promise, it converts it to a string using the force_str function.
            return force_str(obj)
        # If it is not a Promise, it calls the default method of the parent class.
        return super().default(obj)


class CustomModelAdmin(admin.ModelAdmin):
    """
    Base class for customizing ModelAdmin behavior.

    This class provides common customization options and behavior for ModelAdmin classes.
    """
    list_per_page = 10

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        """
        Render the change form for the admin interface.
        This method customizes the rendering of the change form in the admin interface
        and remove the 'show_save_and_continue' and 'show_save_and_add_another' button.
        """
        context.update({
            'show_save_and_continue': False,
            'show_save_and_add_another': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Customize form fields for database fields.
        This method customizes form fields for database fields in the admin interface by
        making view, add and change permission False as default for admin.
        """
        formfield = super().formfield_for_dbfield(db_field, **kwargs)

        if hasattr(formfield, 'widget') and isinstance(formfield.widget, RelatedFieldWidgetWrapper):
            formfield.widget.can_view_related = False
            formfield.widget.can_change_related = False
            formfield.widget.can_add_related = False

        return formfield

    def save_model(self, request, obj, form, change):
        """
        Save the model instance.
        This method saves the model instance and logs changes if any.
        """
        if change:
            old_obj = self.model.objects.get(pk=obj.pk)
            changes = get_changes(old_obj, obj)
            if changes:
                change_message = json.dumps(changes, cls=CustomJSONEncoder)
                log_change(obj, request.user, change_message)
        super().save_model(request, obj, form, change)

    def log_change(self, request, object, message):
        """
        Log changes to the model instance.
        """
        pass


class CustomStackedInline(admin.StackedInline):
    """
    Custom inline class based on admin.StackedInline.

    This class provides common customization options and behavior for stacked inline classes.
    """
    extra = 0
    exclude = ('status',)

    def has_add_permission(self, request, obj=None):
        """
        Disable the add permission.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Disables the change permission.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disables the delete permission.
        """
        return False


class CustomTabularImageInline(admin.TabularInline):
    """
    Custom inline class for managing image models based on admin.TabularInline.
    This class provides customization for managing image models in tabular format.
    """
    extra = 0
    exclude = ("status",)
    readonly_fields = ('image',)
    can_delete = False

    def has_add_permission(self, request, obj=None):
        """
        Disables the add permission.
        """
        return False


class ActivityImageInline(CustomTabularImageInline):
    """
    Inline class for managing ActivityImage models within related models.
    This class provides configuration options for displaying and managing ActivityImage
    models within related models.
    """
    model = ActivityImage
    verbose_name = 'Image'
    verbose_name_plural = 'Images'


class PackageImageInline(CustomTabularImageInline):
    """
    Inline class for managing PackageImage models within related models.
    This class provides configuration options for displaying and managing PackageImage
    models within related models.
    """
    model = PackageImage
    verbose_name = 'Image'
    verbose_name_plural = 'Images'
    readonly_fields = ('thumbnail', 'image',)

    # Display fields
    fields = ('thumbnail', 'image',)


class AttractionImageInline(admin.TabularInline):
    """
    Inline class for managing AttractionImage models within related models.
    This class provides configuration options for displaying and managing AttractionImage
    models within related models.
    """
    model = AttractionImage
    extra = 3
    verbose_name = 'Image'
    verbose_name_plural = 'Images'


class ItineraryInline(CustomStackedInline):
    """
    Inline class for managing Itinerary models within related models.
    This class provides configuration options for displaying and managing Itinerary
    models within related models.
    """
    model = Itinerary
    exclude = ['overview', 'status']
    readonly_fields = ['overview_display']

    def overview_display(self, instance):
        """Custom method to display overview without HTML tags"""
        return strip_tags(instance.overview)
    overview_display.short_description = 'Overview'


class InclusionExclusionInline(CustomStackedInline):
    """
    Inline class for managing InclusionExclusion models within related models.
    This class provides configuration options for displaying and managing InclusionExclusion
    models within related models.
    """
    model = InclusionExclusion
    exclude = ['status']


class InformationsInline(CustomStackedInline):
    """
    Inline class for managing Informations models within related models.
    This class provides configuration options for displaying and managing Informations
    models within related models.
    """
    model = Informations
    exclude = ['status']


class PricingInline(CustomStackedInline):
    """
    Inline class for managing Pricing models within related models.
    This class provides configuration options for displaying and managing Pricing
    models within related models.

    Attributes:
    - model (Model): The Pricing model.
    - exclude (list): Fields to exclude from the inline form.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    - readonly_fields (list): Readonly fields in the inline form.
    """
    model = Pricing
    exclude = ['activity', 'status', 'blackout_dates']
    verbose_name = 'Pricing'
    verbose_name_plural = 'Pricing'
    readonly_fields = ['get_blackout_dates']

    def get_blackout_dates(self, obj):
        """
        Retrieve the formatted blackout dates.
        """
        blackout_data = obj.blackout_dates
        formatted_blackout_dates = []
        if blackout_data:
            if blackout_data.get('weeks'):
                formatted_blackout_dates.append(
                    f"Weekdays: {', '.join(blackout_data['weeks']).title()}")
            if blackout_data.get('custom_date'):
                custom_dates = ', '.join(
                    datetime.strptime(date_str, '%Y-%m-%d').strftime(
                        '%d-%m-%Y') for date_str in blackout_data['custom_date'])
                formatted_blackout_dates.append(f"Custom Dates: {custom_dates}")
            if blackout_data.get('excluded_blackout_dates'):
                excluded_dates = ', '.join(
                    datetime.strptime(date_str, '%Y-%m-%d').strftime(
                        '%d-%m-%Y') for date_str in blackout_data['excluded_blackout_dates'])
                formatted_blackout_dates.append(f"Excluded Dates: {excluded_dates}")
        return '\n'.join(formatted_blackout_dates)
    get_blackout_dates.short_description = 'Blackout Dates'

    def has_change_permission(self, request, obj=None):
        """
        Disables the change permission.
        """
        return False

    def has_add_permission(self, request, obj=None):
        """
        Disables the add permission.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disables the delete permission.
        """
        return False


class CancellationPolicyInline(CustomStackedInline):
    """
    Inline class for managing CancellationPolicy models within related models.
    This class provides configuration options for displaying and managing CancellationPolicy
    models within related models.

    Attributes:
    - model (Model): The CancellationPolicy model.
    - fields (list): Fields to include in the inline form.
    - readonly_fields (list): Readonly fields in the inline form.
    """
    model = CancellationPolicy
    fields = ['cancellation_policies']
    readonly_fields = ['cancellation_policies']

    def cancellation_policies(self, obj):
        """
        Retrieve and format cancellation policies.
        """
        cancellation_categories = []
        policies = CancellationPolicy.objects.filter(package=obj.package)
        for policy in policies:
            categories = policy.category.all()
            for category in categories:
                if category.to_day == 0:
                    category_dict = {
                        'from_day': category.from_day,
                        'amount_percent': category.amount_percent,
                        }
                else:
                    category_dict = {
                        'from_day': category.from_day,
                        'to_day': category.to_day,
                        'amount_percent': category.amount_percent,
                        }
                cancellation_categories.append(category_dict)
        # Render the HTML template with pricing_list
        cancellation_info = render_to_string(
            'admin/cancellation_table_template.html', {
                'cancellation_category': cancellation_categories})
        return mark_safe(cancellation_info)  # Mark the string as safe HTML
    cancellation_policies.short_description = ''


class PackageFaqQuestionAnswerInline(CustomStackedInline):
    """
    Inline class for managing PackageFaqQuestionAnswer models within related models.
    This class provides configuration options for displaying and managing PackageFaqQuestionAnswer
    models within related models.

    Attributes:
    - model (Model): The PackageFaqQuestionAnswer model.
    - template (str): The template to use for rendering the inline form.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    """
    model = PackageFaqQuestionAnswer
    template = 'admin/inline_admin.html'
    verbose_name = 'Faq'
    verbose_name_plural = 'Faq'

class ActivityItineraryInline(CustomStackedInline):
    """
    Inline class for managing ActivityItinerary models within related models.
    This class provides configuration options for displaying and managing ActivityItinerary
    models within related models.

    Attributes:
    - model (Model): The ActivityItinerary model.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    - exclude (list): Fields to exclude from the inline form.
    - readonly_fields (list): Readonly fields in the inline form.
    """
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
    """
    Inline class for managing ActivityInformations models within related models.
    This class provides configuration options for displaying and managing ActivityInformations
    models within related models.

    Attributes:
    - model (Model): The ActivityInformations model.
    - exclude (list): Fields to exclude from the inline form.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    - template (str): The template to use for rendering the inline form.
    """
    model = ActivityInformations
    exclude = ['exclusiondetails', 'status']
    verbose_name = 'Information'
    verbose_name_plural = 'Information'
    template = 'admin/information_tab.html'

    def has_change_permission(self, request, obj=None):
        """
        Disables the change permission.
        """
        return False

    def has_add_permission(self, request, obj=None):
        """
        Disables the add permission.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disables the delete permission.
        """
        return False


class ActivityPricingInline(CustomStackedInline):
    """
    Inline class for managing ActivityPricing models within related models.
    This class provides configuration options for displaying and managing ActivityPricing
    models within related models.

    Attributes:
    - model (Model): The ActivityPricing model.
    - exclude (list): Fields to exclude from the inline form.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    - readonly_fields (list): Readonly fields in the inline form.
    """
    model = Pricing
    exclude = ['package','status', 'blackout_dates']
    verbose_name = 'Pricing'
    verbose_name_plural = 'Pricing'
    readonly_fields = ['get_blackout_dates']

    def get_blackout_dates(self, obj):
        """Retrieve and format blackout dates."""
        blackout_data = obj.blackout_dates
        formatted_blackout_dates = []
        if blackout_data:
            if blackout_data.get('weeks'):
                formatted_blackout_dates.append(
                    f"Weekdays: {', '.join(blackout_data['weeks']).title()}")
            if blackout_data.get('custom_date'):
                custom_dates = ', '.join(
                    datetime.strptime(date_str, '%Y-%m-%d').strftime(
                        '%d-%m-%Y') for date_str in blackout_data['custom_date'])
                formatted_blackout_dates.append(f"Custom Dates: {custom_dates}")
            if blackout_data.get('excluded_blackout_dates'):
                excluded_dates = ', '.join(
                    datetime.strptime(date_str, '%Y-%m-%d').strftime(
                        '%d-%m-%Y') for date_str in blackout_data['excluded_blackout_dates'])
                formatted_blackout_dates.append(f"Excluded Dates: {excluded_dates}")
        return '\n'.join(formatted_blackout_dates)
    get_blackout_dates.short_description = 'Blackout Dates'

    def has_change_permission(self, request, obj=None):
        """
        Disables the add permission.
        """
        return False

    def has_add_permission(self, request, obj=None):
        """
        Disables the add permission.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disables the add permission.
        """
        return False


class ActivityFaqQuestionAnswerInline(CustomStackedInline):
    """
    Inline class for managing ActivityFaqQuestionAnswer models within related models.

    This class provides configuration options for displaying and managing ActivityFaqQuestionAnswer
    models within related models.

    Attributes:
    - model (Model): The ActivityFaqQuestionAnswer model.
    - template (str): The template to use for rendering the inline form.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    """
    model = ActivityFaqQuestionAnswer
    template = 'admin/inline_admin.html'
    verbose_name = 'Faq'
    verbose_name_plural = 'Faq'


class ActivityCancellationPolicyInline(CustomStackedInline):
    """
    Inline class for managing ActivityCancellationPolicy models within related models.

    This class provides configuration options for displaying and managing ActivityCancellationPolicy
    models within related models.

    Attributes:
    - model (Model): The ActivityCancellationPolicy model.
    - fields (list): Fields to include in the inline form.
    - readonly_fields (list): Readonly fields in the inline form.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    """
    model = ActivityCancellationPolicy
    fields = ['cancellation_policies']
    readonly_fields = ['cancellation_policies']
    verbose_name = 'Cancellation Policy'
    verbose_name_plural = 'Cancellation Policies'

    def cancellation_policies(self, obj):
        """Retrieve and format cancellation policies."""
        cancellation_categories = []
        policies = ActivityCancellationPolicy.objects.filter(activity=obj.activity)
        for policy in policies:
            categories = policy.category.all()
            for category in categories:
                if category.to_day == 0:
                    category_dict = {
                        'from_day': category.from_day,
                        'amount_percent': category.amount_percent,
                        }
                else:
                    category_dict = {
                        'from_day': category.from_day,
                        'to_day': category.to_day,
                        'amount_percent': category.amount_percent,
                        }
                cancellation_categories.append(category_dict)
        # Render the HTML template with pricing_list
        cancellation_info = render_to_string(
            'admin/cancellation_table_template.html', {
                'cancellation_category': cancellation_categories})
        return mark_safe(cancellation_info)  # Mark the string as safe HTML
    cancellation_policies.short_description = ''


class UserReviewImageInline(admin.TabularInline):
    """
    Inline class for managing UserReviewImage models within related models.
    This class provides configuration options for displaying and managing UserReviewImage
    models within related models.

    Attributes:
    - model (Model): The UserReviewImage model.
    - readonly_fields (list): Readonly fields in the inline form.
    - can_delete (bool): Whether deletion of instances is allowed.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    """
    model = UserReviewImage
    readonly_fields = ('images',)
    can_delete = False
    verbose_name = 'Images'
    verbose_name_plural = 'Images'

    def has_add_permission(self, request, obj=None):
        """Disables the add permission."""
        return False


class BlogImageInline(admin.TabularInline):
    """
    Inline class for managing BlogImage models within related models.
    This class provides configuration options for displaying and managing BlogImage
    models within related models.

    Attributes:
    - model (Model): The BlogImage model.
    - can_delete (bool): Whether deletion of instances is allowed.
    - extra (int): The number of empty forms to display.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    """
    model = BlogImage
    can_delete = False
    extra = 1
    verbose_name = 'Images'
    verbose_name_plural = 'Images'

    def has_add_permission(self, request, obj=None):
        """Enable the add permission."""
        return True


class AgentBankDetailsInline(CustomStackedInline):
    """
    Inline class for managing AgentBankDetails models within related models.

    This class provides configuration options for displaying and managing AgentBankDetails
    models within related models.

    Attributes:
    - model (Model): The AgentBankDetails model.
    - verbose_name (str): The singular name for the inline.
    - verbose_name_plural (str): The plural name for the inline.
    """
    model = AgentBankDetails
    verbose_name = 'Agent Bank Details'
    verbose_name_plural = 'Agent Bank Details'
