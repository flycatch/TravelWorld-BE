"""
Admin configuration for managing models in the Django admin interface.

This module contains custom admin classes for managing various models in the Django admin interface.
It includes customizations such as defining fieldsets, list displays, search fields, read-only
fields, and other functionalities to enhance the usability of the admin interface.

Additionally, this module imports necessary modules and utilities for admin customization,
such as Django admin modules, template rendering, model resources for import-export functionality,
and color utilities for status indication.

Contents:
    - Django Admin Configurations: CustomModelAdmin, AdminSite
    - Import-Export Functionality: resources, ExportMixin, Field, XLSX
    - Utility Functions: stage_colour, status_colour, booking_status_colour,
        refund_status_colour, account_verification_status_colour
"""
import calendar
from datetime import datetime
from datetime import date

from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from django.contrib.admin import AdminSite
from django.contrib.admin.sites import site
from django.template.defaultfilters import truncatechars
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Count
from django.http import HttpResponse
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError

from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.formats.base_formats import XLSX

from rest_framework.authtoken.models import TokenProxy

from api.tasks import send_email
from api.utils.admin import (
    stage_colour, status_colour, booking_status_colour,
    refund_status_colour, account_verification_status_colour)
from api.common.custom_admin import (
    CustomModelAdmin, ActivityImageInline, PackageImageInline, AttractionImageInline,
    ItineraryInline, InclusionExclusionInline, InformationsInline, PricingInline,
    CancellationPolicyInline, PackageFaqQuestionAnswerInline, ActivityItineraryInline,
    ActivityInformationsInline, ActivityPricingInline, ActivityFaqQuestionAnswerInline,
    ActivityCancellationPolicyInline, UserReviewImageInline, BlogImageInline,
    AgentBankDetailsInline)
from api.models import *
from TravelWorld.settings import ADMIN_REORDER


class AgentAdmin(CustomModelAdmin):
    """
    A custom admin class for managing Agent model instances.

    This class provides various functionalities for the admin interface, including:
        - Fieldsets organization for profile details and permissions.
        - Custom display logic for specific fields like `stage_colour` and
            `account_verification_status_colour`.
        - Setting custom column headers and enabling sorting for specific fields.
        - Disabling the "add" permission for this model in the admin interface.

    Attributes:
        fieldsets (tuple): Sets of fields grouped into sections for display in the admin interface.
        list_display (tuple): Fields to be displayed in the list view of the admin interface.
        list_filter (tuple): Fields used for filtering displayed records in the admin interface.
        search_fields (tuple): Fields used for searching records in the admin interface.
        readonly_fields (tuple): Fields that are read-only in the admin interface.
        inlines (list): Inline classes to be displayed in the admin interface.

    Methods:
        stage_colour: Custom method to display the stage with a specific color.
        account_verification_status_colour: Custom method to display the account verification
            status with a specific color.
        has_add_permission: Determines whether the user has permission to add a new model instance.
    """
    fieldsets = (
        ('Profile Details', {
            'fields': (
                'agent_uid', 'agent_name', 'phone', 'email', 'company_id',
                'company_name', 'company_site', 'message', 'profile_image'
                )}),
        ('Permissions', {
            'fields': (
                'stage', 'account_verification_status'
                )}),
    )

    list_display = ("agent_uid", "company_name", "agent_name", "email", "phone",
                    "stage_colour", "account_verification_status_colour")
    list_filter = ("stage", "account_verification_status")
    search_fields = ("agent_uid", "company_name", "agent_name", "email", "phone")
    readonly_fields = ("agent_uid", "company_id", "company_name", "company_site",
                       "message", "agent_name", "email", "phone", "profile_image")

    inlines = [AgentBankDetailsInline]

    def stage_colour(self, obj):
        """
        Custom method to display the agent's stage with a specific color.
        Returns:
            str: HTML representation of the stage with a specific color.
        """
        return stage_colour(obj.stage)
    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage

    def account_verification_status_colour(self, obj):
        """
        Custom method to display the agent's account verification status with a specific color.
        Returns:
            str: HTML representation of the account verification status with a specific color.
        """
        return stage_colour(obj.account_verification_status)
    # Set a custom column header
    account_verification_status_colour.short_description = 'Account Status'
    # Enable sorting by account_verification_status
    account_verification_status_colour.admin_order_field = 'account_verification_status'

    def has_add_permission(self, request):
        return False


class UserAdmin(CustomModelAdmin):
    """
    A custom admin class for managing User model instances.

    Attributes:
        fieldsets (tuple): Sets of fields grouped into sections for display in the admin interface.
        list_display (tuple): Fields to be displayed in the list view of the admin interface.
        search_fields (tuple): Fields used for searching records in the admin interface.
        change_form_template (str): Path to the custom change form template.

    Methods:
        has_change_permission: Determines whether the user has permission to change a User instance.
        has_add_permission: Determines whether the user has permission to add a new User instance.
    """
    fieldsets = (
        ('Profile Details', {'fields': ('user_uid', 'username', 'first_name',
         'last_name', 'mobile', 'email', 'profile_image')}),
    )

    list_display = ("user_uid", "username", "first_name", "last_name", "email", "mobile")
    search_fields = ("user_uid", "username", "first_name", "last_name", "email", "mobile")
    change_form_template = 'admin/change_form_hidden_history.html'

    def has_change_permission(self, request, obj=None):
        """
        Remove change permission for user interface
        """
        return False

    def has_add_permission(self, request, obj=None):
        """
        Remove add permission for user interface
        """
        return False


class CountryAdmin(CustomModelAdmin):
    """
    A custom admin class for managing Country model instances.

    This class provides a basic configuration for the Country model in the
    admin interface, including:
        - List display: Only the "name" field is displayed in the list view.
        - Search fields: Searching is enabled for the "name" field.
        - Excluded fields: "status" and "image" fields are excluded from the admin interface.
        - Add permission: Users have permission to add new Country instances.
    """
    list_display = ("name",)
    search_fields = ("name",)
    exclude = ("status", "image",)

    def has_add_permission(self, request):
        """
        Add permission for user interface
        """
        return True


class StateAdmin(CustomModelAdmin):
    """
    A custom admin class for managing State model instances.

    This class configures the State model in the admin interface, including:
        - List display: "name" and the related "country" are displayed in the list view.
        - Search fields: Searching is enabled for "name" and "country__name" 
            (searches by country name).
        - Excluded fields: "status" field is excluded from the admin interface.
    """
    list_display = ("name", "country",)
    search_fields = ("name", "country__name")
    exclude = ("status",)


class CityAdmin(CustomModelAdmin):
    """
    A custom admin class for managing City model instances.

    This class provides functionalities for managing City models in the admin interface:
        - List display: "name" and the related "state" are displayed in the list view.
        - Search fields: Searching is enabled for "name" and "state__name" (searches by state name).
        - Excluded fields: "status" field is excluded from the admin interface.
        - Read-only fields: "thumbnail_preview" and "cover_preview" are displayed as read-only.
        - Display fields: Defines the order of fields displayed in the change view,
            including thumbnail/cover image upload fields and their respective preview
            fields, and an "is_popular" boolean field.
    """
    list_display = ("name", "state",)
    search_fields = ("name", "state__name")
    exclude = ("status",)
    readonly_fields = ('thumbnail_preview', 'cover_preview')
    # Display fields
    fields = (
        'name', 'country', 'state', 'thumb_image', 'cover_img',
        'thumbnail_preview', 'cover_preview', 'is_popular')


class InclusionsAdmin(CustomModelAdmin):
    """
    A custom admin class for managing Inclusions model instances.

    This class provides functionalities for managing Inclusions models
    in the admin interface:
        - List display: Displays the "name" field in the list view.
        - Search fields: Enables searching by the "name" field.
        - Excluded fields: Excludes "is_deleted", "package", "activity",
            and "status" fields from the admin interface.
        - Custom change form template: Uses a custom template
            'admin/change_form_hidden_history.html' for the change form.
        - Status colour: Adds a custom column for status with colored
            indicators and allows sorting by status.
        - Custom queryset: Filters the queryset to exclude records where
            "package" or "activity" are not null.
    """
    list_display = ("name",)
    search_fields = ("name",)
    exclude = ("is_deleted", "package", "activity", "status")
    change_form_template = 'admin/change_form_hidden_history.html'

    def get_queryset(self, request):
        """
        Retrieves the base queryset and applies filters to exclude records
        where "package" or "activity" are not null.

        Args:
            request: The HTTP request object.
        Returns:
            QuerySet: The filtered queryset.
        """
        # Get the base queryset
        queryset = super().get_queryset(request)
        # Filter the queryset to exclude exclusions with non-null package and activity
        queryset = queryset.filter(package__isnull=True, activity__isnull=True)
        return queryset


class ExclusionsAdmin(CustomModelAdmin):
    """
    A custom admin class for managing Exclusions model instances.

    This class provides functionalities for managing Exclusions
    models in the admin interface:
        - List display: Displays the "name" field in the list view.
        - Search fields: Enables searching by the "name" field.
        - Excluded fields: Excludes "package", "activity", and "status"
            fields from the admin interface.
        - Custom change form template: Uses a custom template
            'admin/change_form_hidden_history.html' for the change form to hide history button.
        - Custom queryset: Filters the queryset to exclude records where
            "package" or "activity" are not null.
    """
    list_display = ("name",)
    search_fields = ("name",)
    exclude = ("package", "activity", "status")
    change_form_template = 'admin/change_form_hidden_history.html'

    def get_queryset(self, request):
        """
        Retrieves the base queryset and applies filters to exclude records
        where "package" or "activity" are not null.

        Args:
            request: The HTTP request object.
        Returns:
            QuerySet: The filtered queryset.
        """
        # Get the base queryset
        queryset = super().get_queryset(request)
        # Filter the queryset to exclude exclusions with non-null package and activity
        queryset = queryset.filter(package__isnull=True, activity__isnull=True)
        return queryset


class ActivityAdmin(CustomModelAdmin):
    """
    A custom admin class for managing Activity model instances.

    This class provides functionalities for managing Activity models in the admin interface:
        - List display: Displays key fields like "activity_uid", "agent", "truncated_title",
            "tour_class", and "stage_colour".
        - List filter: Enables filtering by "tour_class" and "stage".
        - Search fields: Enables searching by fields like "title", "agent__agent_uid",
            "tour_class", "activities__name", and "activity_uid".
        - Excluded fields: Excludes the "is_submitted" field from the admin interface.
        - Fieldsets: Defines the layout and grouping of fields in the change form.
        - Inlines: Includes related inline models for managing related data within the activity.
        - Custom queryset: Excludes records where the stage is 'in-progress'.
        - Custom form field choices: Customizes choices for the "stage" field.
        - Read-only fields: Dynamically sets read-only fields based on whether the
            object is being added or edited.
        - Custom field methods: Provides formatted strings for pickup and drop times,
            and truncates the title for display.
        - Custom column headers: Sets custom column headers and enables sorting for certain fields.
        - Permissions: Disables add and delete permissions.
    """
    list_display = ("activity_uid", "agent", "truncated_title", "tour_class",
                    "stage_colour",)
    list_filter = ("tour_class", "stage")
    search_fields = ("title", "agent__agent_uid", "tour_class",
                     "activities__name", "activity_uid")
    exclude = ('is_submitted',)

    fieldsets = (
        (None, {
            'fields': ('stage', 'activity_uid', 'title', 'agent', 'tour_class',
                       'duration', 'duration_day', 'duration_night', 'duration_hour',
                       'min_members', 'max_members', 'pickup_point', 'pickup_time_string', 
                       'drop_point', 'drop_time_string', 'locations',
                       'activities', 'suitable_for', 'is_popular')
        }),
    )
    inlines = [ActivityImageInline, ActivityItineraryInline, ActivityInformationsInline,
               ActivityPricingInline, ActivityCancellationPolicyInline,
               ActivityFaqQuestionAnswerInline]

    def get_queryset(self, request):
        """
        Retrieves the base queryset and excludes records where the stage is 'in-progress'.

        Args:
            request: The HTTP request object.
        Returns:
            QuerySet: The filtered queryset.
        """
        queryset = super().get_queryset(request)
        return queryset.exclude(stage='in-progress')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Customizes choices for the "stage" field.

        Args:
            db_field: The database field being customized.
            request: The HTTP request object.
            **kwargs: Additional keyword arguments.
        Returns:
            Field: The customized form field.
        """
        if db_field.name == 'stage':
            kwargs['choices'] = [
                ('approved', 'Approved'), ('pending', 'Pending'), ('rejected', 'Rejected'),]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        Sets read-only fields based on whether the object is being added or edited.

        Args:
            obj: The model instance being edited (None if adding a new instance).
        Returns:
            list: A list of field names that should be read-only.
        """
        if obj:  # obj is not None, so this is an edit
            return [
                field.name for field in self.model._meta.fields
                if field.name not in ['is_submitted', 'stage', 'id', 'updated_on',
                                      'created_on', 'is_popular']
                                      ] + ['pickup_time_string', 'drop_time_string',
                                           'locations', 'activities', 'suitable_for']
        return [field.name for field in self.model._meta.fields
                if field.name not in ['is_submitted', 'stage', 'id', 'updated_on', 'created_on']
                ]

    def pickup_time_string(self, obj):
        """
        Returns a formatted string for the pickup time or None if not available.
        """
        if obj.pickup_time:
            return obj.pickup_time.strftime('%I:%M %p')
        return None  # Return None if pickup_time is None
    pickup_time_string.short_description = 'Pickup Time'  # column header for pickup_string

    def drop_time_string(self, obj):
        """
        Returns a formatted string for the drop time or None if not available.
        """
        if obj.drop_time:
            return obj.drop_time.strftime('%I:%M %p')
        return None  # Return None if drop_time is None
    drop_time_string.short_description = 'Drop Time'  # custom column header for drop_time_string

    def truncated_title(self, obj):
        """
        Truncates the title to 60 characters for display.
        """
        # Truncate title to 60 characters using truncatechars filter
        return truncatechars(obj.title, 60)
    truncated_title.short_description = 'Title'
    truncated_title.admin_order_field = 'title'

    def stage_colour(self, obj):
        """
        Returns a color indicator based on the stage of the activity.
        """
        return stage_colour(obj.stage)
    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class AttractionAdmin(CustomModelAdmin):
    """
    A custom admin class for managing Attraction model instances.

    This class provides functionalities for managing Attraction models in the admin interface:
        - List display: Displays the truncated "title" field in the list view.
        - Search fields: Enables searching by the "title" field.
        - Excluded fields: Excludes the "status" field from the admin interface.
        - Inlines: Includes related inline models for managing related data within the attraction.
        - Status colour: Adds a custom column for status with colored indicators and allows
            sorting by status.
        - Truncated title: Truncates the title for display in the list view.
    """
    list_display = ("truncated_title",)
    search_fields = ("title",)
    exclude = ("status",)
    inlines = [AttractionImageInline]

    def truncated_title(self, obj):
        """
        Truncates the title to 150 characters for display.
        """
        return truncatechars(obj.title, 150)
    truncated_title.short_description = 'Title'
    truncated_title.admin_order_field = 'title'


class PackageAdmin(CustomModelAdmin):
    """
    A custom admin class for managing Package model instances.

    This class provides functionalities for managing Package models in the admin interface:
        - List display: Displays key fields like "package_uid", "agent", "truncated_title",
            "tour_class", and "stage_colour".
        - List filter: Enables filtering by "tour_class" and "stage".
        - Search fields: Enables searching by fields like "title", "agent__agent_uid",
            "agent__first_name", "activities__name", "tour_class", and "package_uid".
        - Excluded fields: Excludes the "is_submitted" field from the admin interface.
        - Fieldsets: Defines the layout and grouping of fields in the change form.
        - Inlines: Includes related inline models for managing related data within the package.
        - Custom queryset: Excludes records where the stage is 'in-progress'.
        - Custom form field choices: Customizes choices for the "stage" field.
        - Read-only fields: Dynamically sets read-only fields based on whether the object
            is being added or edited.
        - Custom field methods: Provides formatted strings for pickup and drop times,
            and truncates the title for display.
        - Custom column headers: Sets custom column headers and enables sorting for certain fields.
        - Permissions: Disables add and delete permissions.
    """
    list_display = ("package_uid", "agent", "truncated_title", "tour_class",
                    "stage_colour",)
    list_filter = ("tour_class", "stage")
    search_fields = ("title", "agent__agent_uid", "agent__first_name",
                     "activities__name", "tour_class", "package_uid")
    exclude = ('is_submitted',)
    fieldsets = (
        (None, {
            'fields': ('stage', 'package_uid', 'title', 'agent', 'tour_class',
                       'duration', 'duration_day', 'duration_night', 'duration_hour',
                       'min_members', 'max_members', 'pickup_point', 'pickup_time_string', 
                       'drop_point', 'drop_time_string', "locations",
                       'activities', 'suitable_for', 'is_popular')
        }),
    )
    inlines = [
        PackageImageInline, ItineraryInline, InclusionExclusionInline, InformationsInline,
        PricingInline, CancellationPolicyInline, PackageFaqQuestionAnswerInline,
        ]

    def get_queryset(self, request):
        """
        Retrieves the base queryset and excludes records where the stage is 'in-progress'.

        Returns:
            QuerySet: The filtered queryset.
        """
        queryset = super().get_queryset(request)
        return queryset.exclude(stage='in-progress')

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Customizes choices for the "stage" field.

        Args:
            db_field: The database field being customized.
            request: The HTTP request object.
            **kwargs: Additional keyword arguments.
        Returns:
            Field: The customized form field.
        """
        if db_field.name == 'stage':
            kwargs['choices'] = [
                ('approved', 'Approved'), ('pending', 'Pending'), ('rejected', 'Rejected'),]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        """
        Sets read-only fields based on whether the object is being added or edited.

        Args:
            obj: The model instance being edited (None if adding a new instance).
        Returns:
            list: A list of field names that should be read-only.
        """
        if obj:  # obj is not None, so this is an edit
            return [field.name for field in self.model._meta.fields
                    if field.name not in [
                        'is_submitted', 'stage', 'id', 'updated_on',
                        'created_on', 'is_popular']
                    ] + [
                        'pickup_time_string', 'drop_time_string',
                        'locations', 'suitable_for', 'activities']
        return [field.name for field in self.model._meta.fields
                if field.name not in [
                    'is_submitted', 'stage', 'id', 'updated_on', 'created_on']]

    def pickup_time_string(self, obj):
        """
        Returns a formatted string for the pickup time  or None if not available.
        """
        if obj.pickup_time:
            return obj.pickup_time.strftime('%I:%M %p')
        return None  # Return None if pickup_time is None
    pickup_time_string.short_description = 'Pickup Time'  # custom column header for pickup_string

    def drop_time_string(self, obj):
        """
        Returns a formatted string for the drop time or None if not available.
        """
        if obj.drop_time:
            return obj.drop_time.strftime('%I:%M %p')
        return None  # Return None if drop_time is None
    drop_time_string.short_description = 'Drop Time'  # Set a custom column header for pickup_string

    def truncated_title(self, obj):
        """
        Truncates the title to 60 characters for display.
        """
        return truncatechars(obj.title, 60)
    truncated_title.short_description = 'Title'
    truncated_title.admin_order_field = 'title'

    def stage_colour(self, obj):
        """
        Returns a color indicator based on the stage of the package.
        """
        return stage_colour(obj.stage)
    stage_colour.short_description = 'stage'  # Set a custom column header
    stage_colour.admin_order_field = 'stage'  # Enable sorting by stage

    def has_add_permission(self, request):
        """
        Disables the add permission.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disables the delete permission.
        """
        return False


class PricingDateFilter(admin.SimpleListFilter):
    """
    A custom admin filter for filtering Booking by month.

    This filter allows users to filter Bookings based on the month of their tour date.
    It generates month names for selection and filters the queryset accordingly.
    """
    title = _('Tour Month')
    parameter_name = 'pricing_date_range'

    def lookups(self, request, model_admin):
        """
        Returns a list of month lookups for the filter dropdown.

        Returns:
            list: A list of tuples where each tuple contains a month number and month name.
        """
        months = [(str(i), calendar.month_name[i]) for i in range(1, 13)]  # Generating month names
        return months

    def queryset(self, request, queryset):
        """
        Filters the queryset based on the selected month.

        Args:
            queryset: The original queryset.
        Returns:
            QuerySet: The filtered queryset.
        """
        if self.value() in [str(i) for i in range(1, 13)]:
            return queryset.filter(tour_date__month=int(self.value()))
            # return queryset.filter(package__pricing_package__start_date__month=int(self.value()))


class PricingYearFilter(admin.SimpleListFilter):
    """
    A custom admin filter for filtering Bookings by year.

    This filter allows users to filter Bookings based on the year of their tour date.
    It generates year selections for the last 10 years and filters the queryset accordingly.
    """
    title = _('Tour Year')
    parameter_name = 'pricing_year'

    def lookups(self, request, model_admin):
        """
        Returns a list of year lookups for the filter dropdown.

        Returns:
            list: A list of tuples where each tuple contains a year.
        """
        current_year = datetime.now().year
        years = [(str(year), str(year)) for year in range(current_year, current_year - 10, -1)]
        return years

    def queryset(self, request, queryset):
        """
        Filters the queryset based on the selected year.

        Args:
            queryset: The original queryset.
        Returns:
            QuerySet: The filtered queryset.
        """
        if self.value():
            return queryset.filter(tour_date__year=self.value())
        return queryset


class BookingResource(resources.ModelResource):
    """
    A custom resource class for exporting Booking model data.

    This class defines the fields to be included in the export, their column names, and
    any custom dehydrate methods needed to format the data appropriately.
    """
    booking_id = Field(attribute='booking_id', column_name='Booking UID')
    display_created_on = Field(attribute='created_on', column_name='Booking date')
    tour_date = Field(attribute='tour_date', column_name='Tour date')
    user_uid = Field(attribute='user__user_uid', column_name='User uid')
    booking_amount = Field(attribute='booking_amount', column_name='Booking amount')
    booking_status = Field(attribute='booking_status', column_name='Booking status')
    package_uid = Field(attribute='package__package_uid', column_name='Package UID')
    activity_uid = Field(attribute='activity__activity_uid', column_name='Activity UID')
    agent_uid = Field(column_name='Agent UID')

    class Meta:
        """
        Meta options for the BookingResource class.

        This class defines metadata options for the BookingResource class,
        including the model to use, the fields to export, and the export order.
        """
        model = Booking
        fields = (
            'booking_id', 'display_created_on', 'tour_date', 'user_uid',
            'booking_amount', 'booking_status', 'package_uid', 'activity_uid',
            'agent_uid'
        )
        export_order = fields

    def dehydrate_display_created_on(self, booking):
        """
        Formats the created_on date to 'YYYY-MM-DD'.

        Args:
            booking: The Booking instance.
        Returns:
            str: Formatted booking creation date.
        """
        return booking.created_on.strftime('%Y-%m-%d')

    def dehydrate_agent_uid(self, booking):
        """
        Retrieves the agent UID based on the associated package or activity.

        Args:
            booking: The Booking instance.
        Returns:
            str: Agent UID or None if no agent is associated.
        """
        if booking.package and booking.package.agent:
            return booking.package.agent.agent_uid
        elif booking.activity and booking.activity.agent:
            return booking.activity.agent.agent_uid
        return None


class BookingAdmin(ExportMixin, CustomModelAdmin):
    """
    A custom admin class for managing Booking model instances.

    This class provides functionalities for managing Booking models in the admin interface,
    including list display, filtering, searching, custom fieldsets, exporting, and more.
    """
    def get_fieldsets(self, request, obj=None):
        """
        Returns the fieldsets to be used in the admin form.

        Args:
            obj: The object being edited or None for the add form.
        Returns:
            tuple: A tuple of fieldsets to be used in the admin form.
        """
        if obj:  # Detail page
            if obj.activity:
                return (
                    (None, {
                        'fields': (
                            'user', 'booking_id', 'activity_uid', 'activity_name',
                            'agent_id', 'agent', 'order_id', 'booking_type', 'booking_amount',
                            'payment_id', 'booking_status', 'display_created_on', 'tour_date',
                            'adult', 'child', 'infant', 'refund_amount')
                    }),
                    ('Pricing', {
                        'fields': ('pricing_section',),
                        }),
                    )
            else:
                return (
                    (None, {
                        'fields': (
                            'user', 'booking_id', 'package_uid', 'package_name',
                            'agent_id', 'agent', 'order_id', 'booking_type', 'booking_amount',
                            'payment_id', 'booking_status', 'display_created_on', 'tour_date', 
                            'adult', 'child', 'infant', 'refund_amount', 'object_id')
                    }),
                    ('Pricing', {
                        'fields': ('pricing_section',),
                        }),
                    )
        else:  # Add page
            return (
                (None, {
                    'fields': (
                        'user', 'package', 'activity',
                        'adult', 'child', 'infant', 'booking_amount', 'order_id',
                        'payment_id', 'booking_status', 'tour_date', 'end_date',
                        'refund_amount', 'pricing', 'is_trip_completed')
                }),
                )
    list_display = ("booking_id", "display_created_on", "tour_date", "user_uid",
                    "package_uid", "activity_uid", "agent_id", "booking_status_colour",)
    list_filter = ("booking_status", PricingDateFilter, PricingYearFilter)  # Add the custom filter

    search_fields = ("booking_id", "created_on", "user__user_uid", "tour_date",
                     "package__package_uid", "activity__activity_uid", "package__agent__agent_uid",
                     "activity__agent__agent_uid")
    exclude = ("status",)
    resource_class = BookingResource
    change_form_template = 'admin/change_form_hidden_history.html'

    def get_queryset(self, request):
        """
        Returns the queryset to be used in the admin interface.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.exclude(booking_status='PENDING').order_by('-tour_date')
        return queryset

    def export_action(self, request, *args, **kwargs):
        """
        Export action for skipping the confirmation page.
        """
        # Get the export format
        file_format = XLSX()

        # Get the filtered queryset
        queryset = self.get_export_queryset(request)

        # Export the filtered queryset
        dataset = self.resource_class().export(queryset)
        response = HttpResponse(
            file_format.export_data(dataset),
            content_type=file_format.CONTENT_TYPE,
        )
        response['Content-Disposition'] = f'attachment; filename="bookings.{file_format.get_extension()}"'
        return response

    def get_urls(self):
        """
        Returns the URLs for the admin interface, including a custom export URL.
        """
        urls = super().get_urls()
        custom_urls = [
            path('export/', self.admin_site.admin_view(self.export_action), name='bookings_export')
        ]
        return custom_urls + urls

    def get_export_queryset(self, request):
        """
        Get the queryset to export, applying any admin filters.
        """
        ChangeList = self.get_changelist(request)
        cl = ChangeList(
            request,
            self.model,
            self.list_display,
            self.list_display_links,
            self.list_filter,
            self.date_hierarchy,
            self.search_fields,
            self.list_select_related,
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
            sortable_by=self.sortable_by,
            search_help_text=self.search_help_text
        )

        return cl.get_queryset(request)

    def pricing_section(self, obj):
        """
        Generates the HTML for the pricing section in the admin detail view.
        """
        pricing_obj = obj.pricing
        if pricing_obj:
            pricing_dict = {
                'Tour Date': pricing_obj.start_date, 'Adults Rate': obj.adults_rate,
                'Child Rate': obj.child_rate, 'Infant Rate': obj.infant_rate,
                }

            # Render the HTML template with pricing_list
            pricing_info = render_to_string(
                'admin/pricing_table_template.html', {'pricing_dict': pricing_dict})
            return mark_safe(pricing_info)  # Mark the string as safe HTML
        else:
            return "No pricing information available."
    pricing_section.short_description = ""

    def agent(self, obj):
        """
        Returns the username of the agent associated with the booking's package.
        """
        return obj.package.agent.username if obj.package else None
    agent.admin_order_field = 'package__agent__username'

    def agent_id(self, obj):
        """
        Returns the agent UID associated with the booking's package or activity.
        """
        if obj.package:
            return obj.package.agent.agent_uid
        elif obj.activity:
            return obj.activity.agent.agent_uid
        else:
            return None
    agent_id.admin_order_field = 'package__agent__agent_uid'
    agent_id.short_description = 'Agent UID'  # Set a custom column header

    def user_uid(self, obj):
        """
        Returns the UID of the user associated with the booking.
        """
        return obj.user.user_uid if obj.user else None
    user_uid.admin_order_field = 'user__user_uid'  # Enable sorting by user_uid

    def package_uid(self, obj):
        """
        Returns the UID of the package associated with the booking.
        """
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"
    package_uid.admin_order_field = 'package__package_uid'  # Enable sorting by user_uid

    def activity_uid(self, obj):
        """
        Returns the UID of the activity associated with the booking.
        """
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"
    activity_uid.admin_order_field = 'activity__activity_uid'  # Enable sorting by user_uid

    def display_created_on(self, obj):
        """
        Returns the creation date of the booking formatted as 'YYYY-MM-DD'.
        """
        return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
    display_created_on.short_description = "Booking date"
    display_created_on.admin_order_field = 'created_on'  # Enable sorting by created_on

    def package_name(self, obj):
        """
        Returns the truncated title of the package associated with the booking.
        """
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"
    package_name.admin_order_field = 'package__title'  # Enable sorting by stage

    def activity_name(self, obj):
        """
        Returns the truncated title of the activity associated with the booking.
        """
        return truncatechars(obj.activity.title if obj.activity else None, 35)
    activity_name.short_description = "Activity Name"

    def booking_status_colour(self, obj):
        """
        Returns the booking status with appropriate color coding.
        """
        return booking_status_colour(obj.booking_status)
    booking_status_colour.short_description = 'Booking Status'  # Set a custom column header
    booking_status_colour.admin_order_field = 'booking_status'  # Enable sorting by stage

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
        Enable the delete permission.
        """
        return True


class UserRefundTransactionAdmin(CustomModelAdmin):
    """
    A custom admin class for managing UserRefundTransaction model instances.

    This class provides functionalities for managing UserRefundTransaction
    models in the admin interface,
    including list display, filtering, searching, custom fieldsets,
    readonly fields, email notifications, and more.
    """
    def get_fieldsets(self, request, obj=None):
        """
        Returns the fieldsets to be used in the admin form.

        Args:
            obj: The object being edited or None for the add form.
        Returns:
            tuple: A tuple of fieldsets to be used in the admin form.
        """
        if obj:  # Detail page
            if obj.activity:
                return (
                    (None, {
                        'fields': (
                            'user', 'refund_uid', 'booking_uid', "booking_amount",
                            'activity_uid', 'activity_name', 'agent', 'agent_uid',
                            "booking_date", 'refund_status', 'refund_amount', 'transaction_date')
                    }),
                    ('Cancellation policy', {
                        'fields': ('cancellation_policies',)
                    }),
                )
            else:
                return (
                    (None, {
                        'fields': (
                            'user', 'refund_uid', 'booking_uid', "booking_amount",
                            'package_uid', 'package_name', 'agent', 'agent_uid',
                            "booking_date", 'refund_status', 'refund_amount', 'transaction_date')
                    }),
                    ('Cancellation policy', {
                        'fields': ('cancellation_policies',)
                    }),
                )
        else:  # Add page
            return (
                (None, {
                    'fields': (
                        'package', 'activity', 'booking', 'refund_status', 'refund_amount', 'user',)
                }),
            )
    list_display = ("booking_uid", "user", "package_uid", "activity_uid",
                    "agent", "agent_uid", "refund_uid", "refund_amount",
                    "refund_status_colour", "display_transaction_date")
    list_filter = ("refund_status",)
    search_fields = ("refund_uid", "booking__booking_id", "user__user_uid",
                     "user__username", "refund_amount", "package__title",
                     "package__package_uid", "activity__activity_uid",
                     "package__agent__username", "activity__agent__username",
                     "package__agent__agent_uid", "activity__agent__agent_uid", "created_on")
    exclude = ('status',)

    def cancellation_policies(self, obj):
        """
        Generates the HTML for the cancellation policies section in the admin detail view.

        Args:
            obj: The UserRefundTransaction instance.
        Returns:
            str: The HTML representation of the cancellation policies section.
        """
        cancellation_categories = []

        if obj.package:
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

        if obj.activity:
            policies = ActivityCancellationPolicy.objects.filter(activity=obj.activity)
            for policy in policies:
                categories = policy.category.all()
                cancellation_categories = []
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

        if not cancellation_categories:
            return "No cancellation policies available."

        # Render the HTML template with pricing_list
        cancellation_info = render_to_string(
            'admin/cancellation_table_template.html', {
                'cancellation_category': cancellation_categories})
        return mark_safe(cancellation_info)  # Mark the string as safe HTML
    cancellation_policies.short_description = ""

    def agent(self, obj):
        """
        Returns the username of the agent associated with the refund's package or activity.
        """
        if obj.package:
            return obj.package.agent.username
        elif obj.activity:
            return obj.activity.agent.username
        else:
            return None
    agent.admin_order_field = 'Agent'  # Enable sorting by stage

    def agent_uid(self, obj):
        """
        Returns the agent UID associated with the refund's package or activity.
        """
        if obj.package:
            return obj.package.agent.agent_uid
        elif obj.activity:
            return obj.activity.agent.agent_uid
        else:
            return None
    agent_uid.admin_order_field = 'Agent UID'  # Enable sorting by stage
    agent_uid.short_description = 'Agent UID'  # Set a custom column header

    def package_uid(self, obj):
        """
        Returns the UID of the package associated with the refund.
        """
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"
    package_uid.admin_order_field = 'package__package_uid'  # Enable sorting by stage

    def activity_uid(self, obj):
        """
        Returns the UID of the activity associated with the refund or
        None if no activity is associated.
        """
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"
    activity_uid.admin_order_field = 'activity__activity_uid'  # Enable sorting by stage

    def package_name(self, obj):
        """
        Returns the truncated title of the package associated with the refund or
        None if no package is associated.
        """
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"
    package_name.admin_order_field = 'package__title'  # Enable sorting by stage

    def activity_name(self, obj):
        """
        Returns the truncated title of the activity associated with the refund or
        None if no activity is associated.
        """
        return truncatechars(obj.activity.title if obj.activity else None, 35)
    activity_name.short_description = "Activity Name"

    def booking_uid(self, obj):
        """
        Returns the booking UID associated with the refund or
        None if no booking is associated.
        """
        return obj.booking.booking_id if obj.booking else None
    booking_uid.short_description = "Booking UID"
    booking_uid.admin_order_field = 'booking__booking_id'  # Enable sorting by stage

    def booking_amount(self, obj):
        """
        Returns the booking amount associated with the refund or
        None if no booking is associated.
        """
        return obj.booking.booking_amount if obj.booking else None
    booking_amount.short_description = "Booking amount"

    def booking_date(self, obj):
        """
        Returns the booking date associated with the refund formatted as 'YYYY-MM-DD' or
        None if no booking is associated.
        """
        return obj.created_on.strftime("%Y-%m-%d") if obj.booking else None
    booking_date.short_description = "Booking date"

    def display_transaction_date(self, obj):
        """
        Returns the transaction date formatted as 'YYYY-MM-DD' or
        a placeholder if no date is available.
        """
        if obj.transaction_date:
            return obj.transaction_date.strftime("%Y-%m-%d")  # Customize the date format as needed
        else:
            return "-"  # Or any other placeholder text
    display_transaction_date.short_description = "Transaction Date"
    display_transaction_date.admin_order_field = 'transaction_date'  # Enable sorting by stage

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Sets readonly fields and renders the change form.
        """
        self.readonly_fields += (
            'refund_uid', 'agent_uid', 'package_uid', 'booking_uid', "booking_date",
            'agent', 'package_name', 'booking_amount', 'cancellation_policies',
            'user', 'activity_uid', 'activity_name')
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """
        Saves the model and sends email notifications if refund status has changed.
        """
        # Get the original object before saving changes
        original_obj = self.model.objects.get(pk=obj.pk) if change else None
        # Save the changes
        super().save_model(request, obj, form, change)

        # Check if refund_status has changed and the new status is either "CANCELLED" or "REFUNDED"
        if change and obj.refund_status in ['CANCELLED', 'REFUNDED'] and obj.refund_status != original_obj.refund_status:
            if obj.refund_status == 'REFUNDED':
                Booking.objects.filter(id=obj.booking_id).update(booking_status=obj.refund_status)
            elif obj.refund_status == 'CANCELLED':
                Booking.objects.filter(id=obj.booking_id).update(booking_status='FAILED')

            subject = "REFUND STATUS"
            message = f"Dear {obj.user.username},\n\nYour Booking has been {obj.refund_status}."
            send_email.delay(subject, message, obj.user.email)

    def refund_status_colour(self, obj):
        """
        Returns the HTML representation of the refund status with color.
        """
        return refund_status_colour(obj.refund_status)
    refund_status_colour.short_description = 'Refund Status'  # Set a custom column header
    refund_status_colour.admin_order_field = 'refund_status'  # Enable sorting by stage

    def has_add_permission(self, request, obj=None):
        """
        Disables the add permission.
        """
        return False


class AgentTransactionSettlementAdmin(CustomModelAdmin):
    """
    A custom admin class for managing AgentTransactionSettlement model instances.

    This class provides various functionalities for the admin interface, including:
        - Conditional fieldsets for displaying relevant fields on detail pages based
            on activity or package existence.
        - Custom display logic for specific fields like `account_verification_status`,
            `pricing_section`, and `cancellation_policies`.
        - Overriding the `change_view` method to make certain fields read-only under
            specific conditions and display error messages.
        - Custom logic in `save_model` to handle transaction ID generation, email notifications,
            and basic validation.
        - Disabling the "add" permission for this model in the admin interface.
    """
    def get_fieldsets(self, request, obj=None):
        """
        Defines fieldsets to be displayed in the admin interface depending on the object
        and page (detail or add).

        Args:
            request (HttpRequest): The current request object.
            obj (AgentTransactionSettlement): The current object being edited (None for add page).

        Returns:
            tuple: A tuple of fieldsets for the admin interface.
        """
        if obj:  # Detail page
            if obj.activity:
                return (
                    (None, {
                        'fields': (
                            'agent_uid', 'transaction_id', 'booking_uid', 'booking_amount',
                            'agent_transaction_booking_type', 'activity_uid', 'activity_name',
                            'display_created_on', 'payment_settlement_status',
                            'payment_settlement_amount', 'payment_settlement_date',
                            )
                    }),
                    ('Pricing', {
                        'fields': ('pricing_section',),
                    }),
                    ('Cancellation Policy', {
                        'fields': ('cancellation_policies',),
                    }),
                )
            else:
                return (
                    (None, {
                        'fields': (
                            'agent_uid', 'transaction_id', 'booking_uid', 'booking_amount',
                            'agent_transaction_booking_type', 'package_uid', 'package_name',
                            'display_created_on', 'payment_settlement_status',
                            'payment_settlement_amount', 'payment_settlement_date',
                            )
                    }),
                    ('Pricing', {
                        'fields': ('pricing_section',),
                    }),
                    ('Cancellation Policy', {
                        'fields': ('cancellation_policies',)
                    }),
                )
        else:  # Add page
            return (
                (None, {
                    'fields': (
                        'package', 'activity', 'booking', 'payment_settlement_status',
                        'payment_settlement_amount', 'agent', 'payment_settlement_date'
                        )
                }),
            )

    list_display = ("booking_uid", "agent_transaction_booking_type", "package_uid", "activity_uid",
                    "agent_uid", "transaction_id", "display_created_on",
                    "payment_settlement_status_colour", "account_verification_status")
    list_filter = ("payment_settlement_status", "booking__booking_type")
    search_fields = ("transaction_id", "booking__booking_id", "booking_type", "package__title",
                     "package__package_uid", "activity__activity_uid", "agent__agent_uid",
                     "agent__username", "payment_settlement_date", "created_on")
    exclude = ('status',)

    def account_verification_status(self, obj):
        """
        Retrieves and displays the account verification status of the related agent.

        Args:
            obj (AgentTransactionSettlement): The current object being edited.

        Returns:
            str: The account verification status of the related agent
                (or None if no agent is related).
        """
        return account_verification_status_colour(
            obj.agent.account_verification_status if obj.agent else None)

    account_verification_status.short_description = "Account Status"
    account_verification_status.admin_order_field = "agent__account_verification_status"

    def pricing_section(self, obj):
        """
        Generates and displays the pricing information related to the booking.

        Args:
            obj (AgentTransactionSettlement): The current object being edited.

        Returns:
            str: The HTML content for displaying the pricing information or a message
                 indicating no pricing information is available.
        """
        pricing_obj = obj.booking.pricing
        if pricing_obj:
            if obj.booking.adults_rate:
                pricing_dict = {'Tour Date': obj.booking.tour_date,
                                'Adult Count': obj.booking.adult,
                                'Adult Rate': obj.booking.adults_rate,
                                'Adult Commission': obj.booking.adults_commission,
                                'Child Count': obj.booking.child,
                                'Child Rate': obj.booking.child_rate,
                                'Child Commission': obj.booking.child_commission, 
                                'Infant Count': obj.booking.infant,
                                'Infant Rate': obj.booking.infant_rate,
                                'Infant Commission': obj.booking.infant_commission,
                                }

            # Render the HTML template with pricing_list
            pricing_info = render_to_string(
                'admin/pricing_table_template.html', {'pricing_dict': pricing_dict})
            return mark_safe(pricing_info)  # Mark the string as safe HTML
        else:
            return "No pricing information available."

    pricing_section.short_description = ""

    def cancellation_policies(self, obj):
        """
        Generates and displays the cancellation policies related to the package or activity.

        Args:
            obj (AgentTransactionSettlement): The current object being edited.

        Returns:
            str: The HTML content for displaying the cancellation policies or a message
                 indicating no cancellation policies are available.
        """
        cancellation_categories = []

        if obj.package:
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

        if obj.activity:
            policies = ActivityCancellationPolicy.objects.filter(activity=obj.activity)
            for policy in policies:
                categories = policy.category.all()
                cancellation_categories = []
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

        if not cancellation_categories:
            return "No cancellation policies available."

        # Render the HTML template with pricing_list
        cancellation_info = render_to_string(
            'admin/cancellation_table_template.html',
            {'cancellation_category': cancellation_categories})
        return mark_safe(cancellation_info)  # Mark the string as safe HTML

    cancellation_policies.short_description = ''

    def agent(self, obj):
        """
        Retrieves the username of the related agent.
        """
        return obj.package.agent.username if obj.package else None

    def agent_uid(self, obj):
        """
        Retrieves the agent UID of the related agent.
        """
        if obj.package:
            return obj.package.agent.agent_uid
        elif obj.activity:
            return obj.activity.agent.agent_uid
        else:
            return None
    agent_uid.short_description = 'Agent UID'  # Set a custom column header
    agent_uid.admin_order_field = 'Agent UID'  # Enable sorting by agent_uid

    def package_uid(self, obj):
        """
        Retrieves the package UID of the related package.
        """
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"
    package_uid.admin_order_field = 'package__package_uid'  # Enable sorting by package__package_uid

    def activity_uid(self, obj):
        """
        Retrieves the activity UID of the related activity.
        """
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"
    activity_uid.admin_order_field = 'activity__activity_uid'  # Enable sorting by activity_uid

    def package_name(self, obj):
        """
        Retrieves the truncated package name of the related package.
        """
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"
    package_name.admin_order_field = 'package__title'  # Enable sorting by package__title

    def activity_name(self, obj):
        """
        Retrieves the truncated activity name of the related activity.
        """
        return truncatechars(obj.activity.title if obj.activity else None, 35)
    activity_name.short_description = "Activity Name"

    def booking_uid(self, obj):
        """
        Retrieves the booking UID of the related booking.
        """
        return obj.booking.booking_id if obj.booking else None
    booking_uid.short_description = "Booking UID"
    booking_uid.admin_order_field = 'booking__booking_id'  # Enable sorting by booking_id

    def booking_amount(self, obj):
        """
        Retrieves the booking Amount of the related booking.
        """
        return obj.booking.booking_amount if obj.booking else None
    booking_amount.short_description = "Booking amount"

    def agent_transaction_booking_type(self, obj):
        """
        Retrieves the booking type of the related booking.
        """
        return obj.booking.booking_type if obj.booking else None
    agent_transaction_booking_type.short_description = "Booking type"
    agent_transaction_booking_type.admin_order_field = "booking_type"

    def display_created_on(self, obj):
        """
        Retrieves the formatted transaction date for display.
        Returns:
            str: The formatted transaction date.
        """
        return obj.created_on.strftime("%Y-%m-%d")  # Customize the date format as needed
    display_created_on.short_description = "Transaction date"
    display_created_on.admin_order_field = 'created_on'  # Enable sorting by created_on

    def payment_settlement_status_colour(self, obj):
        """
        Retrieves the color representation of the payment settlement status.
        Returns:
            str: The color representation of the payment settlement status.
        """
        return refund_status_colour(obj.payment_settlement_status)
    # Set a custom column header
    payment_settlement_status_colour.short_description = 'Payment settlement status'
    # Enable sorting by payment_settlement_status
    payment_settlement_status_colour.admin_order_field = 'payment_settlement_status'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Overriding default change view to make readonly fields and
        check agent bank approved status and show message if not approved
        and restrict editing fields.
        """
        # Get the object based on the object_id
        obj = self.get_object(request, object_id)

        # Define the initial set of read-only fields
        self.readonly_fields = [
            'transaction_id', 'agent_uid', 'package_uid', 'booking_uid', 'agent',
            'display_created_on', 'package_name', 'booking_amount', 'agent_transaction_booking_type',
            'cancellation_policies', 'pricing_section', 'activity_uid', 'activity_name']

        # Check if the object exists and if the agent's account verification status is not approved
        if obj and obj.agent and obj.agent.account_verification_status != 'approved':
            # Add additional read-only fields if the condition is met
            self.readonly_fields += ['payment_settlement_status',
                                     'payment_settlement_amount',
                                     'payment_settlement_date']
            # Display error message when agent bank account is not approved
            messages.error(request, "Bank Account Not verified.")

        # Call the parent class's change_view method
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """
        Overrides the default `save_model` behavior to perform additional 
        actions before saving changes to the model instance.

        Args:
            request (HttpRequest): The current request object.
            obj (AgentTransactionSettlement): The object being saved.
            form (ModelForm): The model form used for data collection.
            change (bool): Whether the object is being created (False) or updated (True).
        """
        # Call the model's clean method to perform validation
        obj.full_clean()

        # Get the original object before saving changes
        original_obj = self.model.objects.get(pk=obj.pk) if change else None
        # Save the changes
        super().save_model(request, obj, form, change)

        if change and obj.payment_settlement_status in ['SUCCESSFUL'] and obj.payment_settlement_status != original_obj.payment_settlement_status:
            obj.transaction_id = f"EWTRAN-{obj.id}"
            obj.save()

        subject = "EXPLORE WORLD | TRANSACTION"
        message = f"Dear {obj.agent.agent_uid},\n\nYour transaction settlement has been {obj.payment_settlement_status}."
        send_email.delay(subject, message, obj.agent.email)

    def has_add_permission(self, request, obj=None):
        """
        Remove add permission for admin interface
        """
        return False


class UserReviewAdmin(CustomModelAdmin):
    """
    A custom admin class for managing UserReview model instances.

    This class provides functionalities for managing UserReview models
    in the admin interface,
    including list display, filtering, searching, custom fieldsets, readonly fields,
    inline image management, and custom change form templates.
    """
    list_display = ("user", "package_uid", "activity_uid", "rating")
    search_fields = ("package__package_uid", "activity__activity_uid", "user__user_uid")
    list_filter = ("rating",)
    exclude = ('status', 'is_deleted', 'is_active')
    readonly_fields = ("package_uid", "activity_name", "package_name")
    fieldsets = (
        (None, {
            'fields': ("user", "package", "rating", "review",
                       "booking", "agent", "agent_comment",)
        }),
        )
    inlines = [UserReviewImageInline]
    change_form_template = 'admin/change_form_hidden_history.html'

    def get_fieldsets(self, request, obj=None):
        """
        Returns the fieldsets to be used in the admin form.

        Args:
            obj: The object being edited or None for the add form.
        Returns:
            tuple: A tuple of fieldsets to be used in the admin form.
        """
        if obj:  # Detail page
            if obj.activity:
                return (
                    (None, {
                        'fields': (
                            "user", "activity_uid", "activity_name", "rating", "review",
                            "booking", "agent", "agent_comment",)
                    }),
                )
            else:
                return (
                    (None, {
                        'fields': (
                            "user", "package_uid", "package_name", "rating", "review",
                            "booking", "agent", "agent_comment",)
                    }),
                )
        else:  # Add page
            return (
                (None, {
                    'fields': ("user", "package", "rating", "review",
                               "booking", "agent", "agent_comment",)
                        }),
                )

    def package_uid(self, obj):
        """
        Returns the UID of the package associated with the review or
        None if no package is associated.
        """
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"
    package_uid.admin_order_field = 'package__package_uid'  # Enable sorting by user_uid

    def activity_uid(self, obj):
        """
        Returns the UID of the activity associated with the review or
        None if no activity is associated.
        """
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"
    activity_uid.admin_order_field = 'activity__activity_uid'  # Enable sorting by user_uid

    def package_name(self, obj):
        """
        Returns the truncated title of the package associated with the review or
        None if no package is associated.
        """
        return truncatechars(obj.package.title if obj.package else None, 35)
    package_name.short_description = "Package Name"

    def activity_name(self, obj):
        """
        Returns the truncated title of the activity associated with the review or
        None if no activity is associated.
        """
        return truncatechars(obj.activity.title if obj.activity else None, 35)
    activity_name.short_description = "Activity Name"

    def has_add_permission(self, request, obj=None):
        """
        Remove add permission for admin interface
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Remove change permission for admin interface
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Enable delete permission for admin interface
        """
        return True


class AdvanceAmountPercentageSettingAdmin(CustomModelAdmin):
    """
    Admin class for managing AdvanceAmountPercentageSetting model instances.

    This class provides functionalities for managing AdvanceAmountPercentageSetting
    models in the admin interface,
    including list display and custom permission settings to restrict adding and deleting.
    """
    list_display = ("id", "percentage")

    def has_add_permission(self, request):
        """
        Disable change permission for admin interface
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disable change permission for admin interface
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Enable change permission for admin interface
        """
        return True


class PackageCategoryAdmin(CustomModelAdmin):
    """
    Admin class for managing PackageCategory model instances.

    This class provides functionalities for managing PackageCategory models in the admin interface,
    including list display, search functionality, and a custom change form template.
    """
    list_display = ("name",)
    search_fields = ("name",)
    exclude = ('status',)
    change_form_template = 'admin/change_form_hidden_history.html'


def dashboard_page(request):
    """
    Renders the custom admin dashboard with various statistics and charts.

    This view function fetches data related to users, bookings, agents, agent transactions,
    and user transactions. It aggregates this data and prepares it for display in cards and
    bar charts on the admin dashboard.

    Parameters:
    request (HttpRequest): The request object used to generate the response.

    Returns:
    HttpResponse: The response object containing the rendered admin dashboard
        template with context data.
    """
    total_user_count = User.objects.count()

    # Booking
    total_bookings_count = Booking.objects.exclude(booking_status='PENDING').count()
    successful_bookings = Booking.objects.filter(booking_status='SUCCESSFUL').count()
    failed_bookings = Booking.objects.filter(booking_status='FAILED').count()
    refunded_bookings = Booking.objects.filter(booking_status='REFUNDED').count()
    refund_requested = Booking.objects.filter(booking_status='REFUNDED REQUESTED').count()

    # Agents
    total_agent_count = Agent.objects.count()
    pending_agents = Agent.objects.filter(stage='pending').count()
    approved_agents = Agent.objects.filter(stage='approved').count()
    rejected_agents = Agent.objects.filter(stage='rejected').count()

    # Agent Transactions
    total_agent_transaction_count = AgentTransactionSettlement.objects.count()
    successful_agent_transaction_count = AgentTransactionSettlement.objects.filter(
        payment_settlement_status='SUCCESSFUL').count()
    rejected_agent_transaction_count = AgentTransactionSettlement.objects.filter(
        payment_settlement_status='REJECTED').count()
    pending_agent_transaction_count = AgentTransactionSettlement.objects.filter(
        payment_settlement_status='PENDING').count()

    # User Transactions
    total_user_transaction_count = UserRefundTransaction.objects.count()
    refunded_user_transaction_count = UserRefundTransaction.objects.filter(
        refund_status='REFUNDED').count()
    rejected_user_transaction_count = UserRefundTransaction.objects.filter(
        refund_status='REJECTED').count()
    pending_user_transaction_count = UserRefundTransaction.objects.filter(
        refund_status='PENDING').count()

    cards = {
        'total_bookings_count': total_bookings_count,
        'total_agent_count': total_agent_count,
        'total_user_count': total_user_count,
        'successful_bookings': successful_bookings,
        'failed_bookings': failed_bookings,
        'refunded_bookings': refunded_bookings,
        'refund_requested': refund_requested,
        'pending_agents': pending_agents,
        'approved_agents': approved_agents,
        'rejected_agents': rejected_agents,
        'total_agent_transaction_count': total_agent_transaction_count,
        'successful_agent_transaction_count': successful_agent_transaction_count,
        'rejected_agent_transaction_count': rejected_agent_transaction_count,
        'pending_agent_transaction_count': pending_agent_transaction_count,
        'total_user_transaction_count': total_user_transaction_count,
        'refunded_user_transaction_count': refunded_user_transaction_count,
        'rejected_user_transaction_count': rejected_user_transaction_count,
        'pending_user_transaction_count': pending_user_transaction_count
    }

    current_year = datetime.now().year
    months = [calendar.month_name[i] for i in range(1, 13)]
    month_abbreviations = {'January': 'Jan', 'February': 'Feb', 'March': 'Mar',
                           'April': 'Apr', 'May': 'May', 'June': 'Jun', 'July': 'Jul',
                           'August': 'Aug', 'September': 'Sep', 'October': 'Oct',
                           'November': 'Nov', 'December': 'Dec'}

    bar_graph_selected_year = request.GET.get('bar_graph_year', current_year)
    if bar_graph_selected_year:
        bar_graph_selected_year = int(bar_graph_selected_year)
        bar_graph_start_date = datetime(bar_graph_selected_year, 1, 1)
        bar_graph_end_date = datetime(bar_graph_selected_year, 12, 31)

        # Filter bookings based on agent_status if provided in the URL
        agent_stage_filter = request.GET.get('agent_stage_status')
        if agent_stage_filter:
            bookings_count_by_month = Agent.objects.filter(
                created_on__range=[bar_graph_start_date, bar_graph_end_date],
                stage=agent_stage_filter
            ).values('created_on__month').annotate(count=Count('id'))
        else:
            # Use the original query if no filter is provided
            bookings_count_by_month = Agent.objects.filter(
                created_on__range=[bar_graph_start_date, bar_graph_end_date]
            ).values('created_on__month').annotate(count=Count('id'))

        agent_chart_booking = [
            {
                'month': calendar.month_name[item['created_on__month']],
                'count': item['count']
            }
            for item in bookings_count_by_month
        ]

        agent_month_counts = {item['month']: item['count'] for item in agent_chart_booking}

        # Populate barchart_booking with counts for all months
        agent_chart_booking = [
            {'month': month, 'count': agent_month_counts.get(month, 0)}
            for month in months
        ]

    selected_year = request.GET.get('year',current_year)
    if selected_year:
        selected_year = int(selected_year)
        start_date = datetime(selected_year, 1, 1)
        end_date = datetime(selected_year, 12, 31)

        # Filter bookings based on booking_status if provided in the URL
        booking_status_filter = request.GET.get('booking_status')
        if booking_status_filter:
            bookings_count_by_month = Booking.objects.filter(
                created_on__range=[start_date, end_date], booking_status=booking_status_filter
            ).values('created_on__month').annotate(count=Count('id'))
        else:
            # Use the original query if no filter is provided
            bookings_count_by_month = Booking.objects.filter(
                created_on__range=[start_date, end_date]
            ).values('created_on__month').annotate(count=Count('id'))

        barchart_booking = [
            {
                'month': calendar.month_name[item['created_on__month']],
                'count': item['count']
            }
            for item in bookings_count_by_month
        ]

        month_counts = {item['month']: item['count'] for item in barchart_booking}

        # Populate barchart_booking with counts for all months
        barchart_booking = [
            {'month': month, 'count': month_counts.get(month, 0)}
            for month in months
        ]

    # Create list of years for year filter
    current_year = date.today().year
    years_list = [str(year) for year in range(current_year, current_year - 11, -1)]

    for month_dict in barchart_booking:
        month_dict['month'] = month_abbreviations[month_dict['month']]
    for month_dict in agent_chart_booking:
        month_dict['month'] = month_abbreviations[month_dict['month']]

    context = {
        'cards': cards,
        'barchart_booking': barchart_booking,
        'agent_chart_booking': agent_chart_booking,
        'years_list': years_list}

    admin_site: AdminSite = site
    context_data = admin_site.each_context(request)

    # Initialize an empty list to store the reordered available apps
    reordered_available_apps = []

    # Create a dictionary to map model names to their positions in ADMIN_REORDER
    model_order_map = {}
    for idx, item in enumerate(ADMIN_REORDER):
        for model_name in item['models']:
            model_order_map[model_name] = idx

    # Iterate through the ADMIN_REORDER settings
    for item in ADMIN_REORDER:
        # Get the app_label and models for the current item
        models = item['models']

        # Find the corresponding available app using app_label
        for available_app in context_data['available_apps']:
            # Filter and reorder models for the current app based on
            # the models in the ADMIN_REORDER setting
            reordered_models = []
            for model_name in models:
                for model_info in available_app['models']:
                    model_class = model_info['model']
                    current_model_name = f"{model_class._meta.app_label}.{model_class.__name__}"
                    if current_model_name == model_name:
                        reordered_models.append(model_info)
                        break

            reordered_available_apps.append({
                'name': item['label'],
                'app_label': item['app'],
                'app_url': '/admin/api/',
                'has_module_perms': True,
                'models': reordered_models
            })
            break

    context_data['available_apps'] = reordered_available_apps

    # Update the context with the modified context data
    context.update(**context_data)
    return render(request, 'admin/admin_dashboard.html', context=context)


class CoverPageInputForm(forms.ModelForm):
    """
    A form for creating and updating CoverPageInput instances.

    This form is based on the CoverPageInput model and includes all its fields.
    It also includes custom validation for the 'satisfaction' field to ensure
    that its value is between 0 and 100.

    Methods:
    clean_satisfaction(): Validates the 'satisfaction' field to ensure it is between 0 and 100.
    """
    class Meta:
        """
        Meta options for the CoverPageInputForm.

        Attributes:
        model (CoverPageInput): The model that this form is associated with.
        fields (str): Specifies that all fields from the model should be included in the form.
        """
        model = CoverPageInput
        fields = "__all__"

    def clean_satisfaction(self):
        """
        Validates the 'satisfaction' field.

        Ensures that the value of 'satisfaction' is a decimal number between 0 and 100.
        Raises a ValidationError if the value is outside this range.
        """
        satisfaction = self.cleaned_data.get('satisfaction')
        if satisfaction is not None and not (0 <= satisfaction <= 100):
            raise ValidationError(
                _('Satisfaction must be a decimal number between 0 and 100.'),
                code='invalid'
            )
        return satisfaction


class CoverPageInputAdmin(CustomModelAdmin):
    """
    Admin interface for managing CoverPageInput instances.

    This admin class customizes the display and editing of CoverPageInput
    model instances in the Django admin site. It includes configurations
    for displaying certain fields.

    Attributes:
    list_display (tuple): Fields to display in the admin list view.
    fieldsets (tuple): Fieldsets for organizing fields in the admin detail view.
    form (ModelForm): Custom form to use for the model.
    """
    list_display = ("id", "experience", "clients", "satisfaction")
    fieldsets = (
        (None, {
            'fields': ("experience", "clients", "satisfaction")
        }),
        ('Cover Images', {
            'fields': ("activity_image", "package_image", "attraction_image", "product_image")
        }),
    )
    form = CoverPageInputForm

    def has_add_permission(self, request):
        """
        Disable the add permission.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disable the delete permission.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Enable the change permission.
        """
        return True


class SendEnquiryAdmin(CustomModelAdmin):
    """
    Admin interface for managing SendEnquiry instances.

    This admin class customizes the display and management of SendEnquiry
    model instances in the Django admin site. It includes configurations
    for displaying certain fields in the list view, enabling search fields,
    and restricting add and change permissions.

    Attributes:
    list_display (tuple): Fields to display in the admin list view.
    search_fields (tuple): Fields to include in the admin search functionality.
    change_form_template (str): Template to use for the change form.

    Methods:
    package_uid(obj): Returns the package UID for the given SendEnquiry instance.
    activity_uid(obj): Returns the activity UID for the given SendEnquiry instance.
    has_add_permission(request): Disables the add permission.
    has_delete_permission(request, obj=None): Enables the delete permission.
    has_change_permission(request, obj=None): Disables the change permission.
    """
    list_display = ("name", "email", "package_uid", "activity_uid")
    search_fields = ("package__package_uid", "activity__activity_uid", "name", "email")
    change_form_template = 'admin/change_form_hidden_history.html'

    def package_uid(self, obj):
        """
        Returns the package UID for the given SendEnquiry instance if available, else None.
        """
        return obj.package.package_uid if obj.package else None
    package_uid.short_description = "Package UID"
    package_uid.admin_order_field = 'package__package_uid'  # Enable sorting by package_uid

    def activity_uid(self, obj):
        """
        Returns the activity UID for the given SendEnquiry instance if available, else None.
        """
        return obj.activity.activity_uid if obj.activity else None
    activity_uid.short_description = "Activity UID"
    activity_uid.admin_order_field = "activity__activity_uid"  # Enable sorting by activity_uid

    def has_add_permission(self, request):
        """
        Disable the add permission.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Enable the delete permission.
        """
        return True

    def has_change_permission(self, request, obj=None):
        """
        Disable the change permission.
        """
        return False


class SuitableForAdmin(CustomModelAdmin):
    """
    Admin interface for managing SuitableFor instances.

    This admin class customizes the display and management of SuitableFor
    model instances in the Django admin site. It includes configurations
    for displaying certain fields in the list view and enabling search fields.

    Attributes:
    list_display (tuple): Fields to display in the admin list view.
    search_fields (tuple): Fields to include in the admin search functionality.
    change_form_template (str): Template with hidden history button.
    """
    list_display = ("name",)
    search_fields = ("name",)
    change_form_template = 'admin/change_form_hidden_history.html'


class CurrencyAdmin(CustomModelAdmin):
    """
    Admin interface for managing Currency instances.

    This admin class customizes the display and management of Currency
    model instances in the Django admin site. It includes configurations
    for displaying certain fields in the list view, enabling search fields,
    and excluding certain fields from the form.

    Attributes:
    list_display (tuple): Fields to display in the admin list view.
    search_fields (tuple): Fields to include in the admin search functionality.
    exclude (tuple): Fields to exclude from the admin form.
    change_form_template (str): Template with hidden history button.
    """
    list_display = ("name",)
    search_fields = ("name",)
    exclude = ('status',)
    change_form_template = 'admin/change_form_hidden_history.html'


class BaseUserAdmin(CustomModelAdmin):
    """
    Custom Admin for managing BaseUser model.

    This admin class provides a custom interface for managing BaseUser instances,
    used for changing admin basic details on "see more" option.
    It includes specified fields and disables the delete permission.
    After saving changes, it redirects to the admin dashboard.

    Attributes:
        fields (tuple): The fields to be included in the admin interface.
        change_form_template (str): The template used for rendering the change form.
    """
    # Included fields
    fields = ('unique_username', 'first_name', 'last_name', 'phone')
    list_display = ('unique_username', 'first_name', 'last_name', 'phone')
    change_form_template = 'admin/change_form_hidden_history.html'

    def get_readonly_fields(self, request, obj=None):
        """
        Return the readonly fields based on the current user.

        If the logged-in user is not the same as the user being edited, make all fields readonly.
        """
        if obj is not None and obj == request.user:
            return ()
        else:
            return self.fields

    def get_queryset(self, request):
        """
        Return the queryset for this admin.

        Limit the queryset to only include BaseUser instances where is_superuser is True.
        """
        queryset = super().get_queryset(request)
        return queryset.filter(is_superuser=True)


class BlogsAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Blog instances.

    This admin class customizes the display and management of Blog model
    instances in the Django admin site. It includes an inline interface
    for managing related BlogImage instances within the same form.

    Attributes:
    inlines (list): A list of inline models to include in the Blog admin form.
    """
    inlines = [BlogImageInline]


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
admin.site.register(Booking,BookingAdmin)
# admin.site.register(Transaction,TransactionAdmin)

admin.site.register(PackageCategory, PackageCategoryAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(UserReview, UserReviewAdmin)

admin.site.register(CancellationPolicy)
admin.site.register(PackageCancellationCategory)
admin.site.register(ActivityCancellationCategory)
admin.site.register(ActivityCancellationPolicy)
admin.site.register(CoverPageInput, CoverPageInputAdmin)
admin.site.register(Itinerary)
admin.site.register(SuitableFor, SuitableForAdmin)
admin.site.register(SendEnquiry,SendEnquiryAdmin)

admin.site.register(Pricing)
admin.site.register(BlogCategory)
admin.site.register(BlogImage)
admin.site.register(Blogs,BlogsAdmin)


admin.site.register(AdvanceAmountPercentageSetting, AdvanceAmountPercentageSettingAdmin)
admin.site.register(AgentTransactionSettlement, AgentTransactionSettlementAdmin)
admin.site.register(UserRefundTransaction, UserRefundTransactionAdmin)
admin.site.register(BaseUser, BaseUserAdmin)
