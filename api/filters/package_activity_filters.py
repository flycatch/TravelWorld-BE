from api.models import (Package, Activity)
from django_filters import rest_framework as django_filters



class PackageFilter(django_filters.FilterSet):
    stage = django_filters.CharFilter(field_name='stage', lookup_expr='exact')
    tour_class = django_filters.CharFilter(field_name='tour_class', lookup_expr='exact')
    state = django_filters.CharFilter(field_name='state', lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category', lookup_expr='exact')
    is_popular = django_filters.BooleanFilter(field_name='is_popular', lookup_expr='exact')
    duration_filter = django_filters.CharFilter(method='filter_by_duration')



    class Meta:
        model = Package
        fields = ['tour_class', 'stage', 'state', 'category', 'is_popular']


    def filter_by_duration(self, queryset, name, value):
        if value == 'full_day':
            return queryset.filter(duration='day', duration_day=1, duration_night=1)
        elif value == 'multi_day':
            return queryset.filter(duration='day', duration_day__gt=1, duration_night__gt=1)
        return queryset


class ActivityFilter(django_filters.FilterSet):
    stage = django_filters.CharFilter(field_name='stage', lookup_expr='exact')
    tour_class = django_filters.CharFilter(field_name='tour_class', lookup_expr='exact')
    state = django_filters.CharFilter(field_name='state', lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category', lookup_expr='exact')
    is_popular = django_filters.BooleanFilter(field_name='is_popular', lookup_expr='exact')
    
    class Meta:
        model = Activity
        fields = ['tour_class', 'stage', 'state', 'category', 'is_popular']
