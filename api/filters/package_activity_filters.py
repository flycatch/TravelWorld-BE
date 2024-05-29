"""
Module for defining custom filter sets for Package, Activity, and PackageCategory models.

This module includes:
- FilterMixin: A mixin class with custom filter methods.
- PackageFilter: A filter set for filtering packages based on various criteria.
- ActivityFilter: A filter set for filtering activities based on various criteria.
- PackageCategoryFilter: A filter set for filtering package categories based on their popularity.

Classes:
    - FilterMixin: Contains custom filter methods for filtering querysets based on activities
        and duration.
    - PackageFilter: Filter set for Package model.
    - ActivityFilter: Filter set for Activity model.
    - PackageCategoryFilter: Filter set for PackageCategory model.

"""
import ast
from django.db.models import Q
from django_filters import rest_framework as django_filters

from api.models import (Package, Activity, PackageCategory)
from api.filters.general_filters import CustomBooleanFilter


class FilterMixin:
    """
    Mixin class providing custom filter methods.

    Methods:
        - filter_by_activities: Filters a queryset based on provided activity IDs.
        - filter_by_duration: Filters a queryset based on the duration category.
    """
    def filter_by_activities(self, queryset, name, value):
        """
        Filters a queryset based on provided activities IDs.

        This method expects a list of activities IDs (integers) as the `value` parameter.
        It returns a filtered queryset containing only objects where the `activities` field
        (assumed to be a ManyToManyField) is related to at least one of the provided IDs.

        Args:
            queryset: The base queryset to be filtered.
            name: The filter name (unused in this method).
            value: A list of activities IDs (integers).

        Returns:
            The filtered queryset containing objects related to any of the provided activities IDs.
            Duplicates are removed using `distinct()`.

        Raises:
            ValueError: If the `value` cannot be evaluated as a list.
        """
        try:
            # Convert str to list
            activities_ids = ast.literal_eval(value)
            if not isinstance(activities_ids, list):
                raise ValueError("activities value must be a list of integers")
        except (SyntaxError, ValueError):
            return queryset.none()  # Return empty queryset on parsing errors

        filtered_queryset = queryset.filter(activities__id__in=activities_ids)
        return filtered_queryset.distinct()

    def filter_by_duration(self, queryset, name, value):
        """
        Custom method to filter queryset by duration.

        This method filters activities/packages based on three duration categories:

        - full_day: activities/packages lasting a full day (duration='day', duration_day=1,
            duration_night=1) or over 12 hours (duration='hour', duration_hour__gt=12)
        - multi_day: activities/packages lasting more than one day (duration='day',
            duration_day__gt=1, duration_night__gt=1) orover 24 hours (duration='hour',
            duration_hour__gt=24)
        - half_day: activities/packages lasting less than or equal to 12 hours (duration='hour',
            duration_hour__lte=12)

        Args:
            queryset: The base queryset of activities/packages.
            name: The filter name (unused in this method).
            value: The duration filter value ('full_day', 'multi_day', or 'half_day').

        Returns:
            The filtered queryset of activities/packages.
        """
        if value == 'full_day':
            return queryset.filter(Q(duration='day', duration_day=1, duration_night=1) | Q(duration='hour', duration_hour__gt=12))
        elif value == 'multi_day':
            return queryset.filter(Q(duration='day', duration_day__gt=1, duration_night__gt=1) | Q(duration='hour', duration_hour__gt=24))
        elif value == 'half_day':
            return queryset.filter(duration='hour', duration_hour__lte=12)
        return queryset


class PackageFilter(FilterMixin, django_filters.FilterSet):
    """
    Filter for various fields in the Package model.

    This filter set allows you to filter packages based on different criteria,
    including stage, tour class, location (state and city), activities, suitable for,
    popularity, duration, and recommendation status.
    """
    stage = django_filters.CharFilter(field_name='stage', lookup_expr='exact')
    tour_class = django_filters.CharFilter(field_name='tour_class', lookup_expr='exact')
    package_class = django_filters.CharFilter(field_name='package_class', lookup_expr='exact')
    state = django_filters.CharFilter(field_name='locations__state', lookup_expr='exact')
    activities = django_filters.CharFilter(method='filter_by_activities')
    suitable_for = django_filters.CharFilter(field_name='suitable_for', lookup_expr='exact')
    is_popular = django_filters.BooleanFilter(field_name='is_popular', lookup_expr='exact')
    duration_filter = django_filters.CharFilter(method='filter_by_duration')
    city = django_filters.CharFilter(field_name='locations__destinations', lookup_expr='exact')
    is_recommended = django_filters.BooleanFilter(field_name='is_recommended', lookup_expr='exact')

    class Meta:
        """
        Meta options for AttractionFilter.

        **Attributes:**
        * model (api.models): The model that this filter set is based on.
        * fields (list): The list of fields that this filter set can filter on.
        """
        model = Package
        fields = ['tour_class', 'stage', 'state', 'activities',
                  'suitable_for', 'is_popular', 'is_recommended',
                  'package_class']


class ActivityFilter(FilterMixin, django_filters.FilterSet):
    """
    Filter for various fields in the Activity model.

    This filter set allows you to filter activities based on different criteria,
    including stage, tour class, location (state and city), activity type, suitable for,
    popularity, duration, and recommendation status.
    """
    stage = django_filters.CharFilter(field_name='stage', lookup_expr='exact')
    tour_class = django_filters.CharFilter(field_name='tour_class', lookup_expr='exact')
    state = django_filters.CharFilter(field_name='locations__state', lookup_expr='exact')
    activities = django_filters.CharFilter(method='filter_by_activities')
    suitable_for = django_filters.CharFilter(field_name='suitable_for', lookup_expr='exact')
    is_popular = django_filters.BooleanFilter(field_name='is_popular', lookup_expr='exact')
    duration_filter = django_filters.CharFilter(method='filter_by_duration')
    city = django_filters.CharFilter(field_name='locations__destinations', lookup_expr='exact')
    is_recommended = django_filters.BooleanFilter(field_name='is_recommended', lookup_expr='exact')

    class Meta:
        """
        Meta options for AttractionFilter.

        **Attributes:**
        * model (api.models): The model that this filter set is based on.
        * fields (list): The list of fields that this filter set can filter on.
        """
        model = Activity
        fields = ['tour_class', 'stage', 'state', 'activities',
                  'suitable_for', 'is_popular', 'is_recommended']


class PackageCategoryFilter(django_filters.FilterSet):
    """
    Filter for PackageCategory objects based on their is_popular.

    **Fields:**
    * is_popular (CustomBooleanFilter): Filters is_popular by true or false value.
    """
    is_popular = CustomBooleanFilter(field_name='is_popular', lookup_expr='exact')

    class Meta:
        """
        Meta options for AttractionFilter.

        **Attributes:**
        * model (api.models): The model that this filter set is based on.
        * fields (list): The list of fields that this filter set can filter on.
        """
        model = PackageCategory
        fields = ['is_popular']
