from api.models import (Package, Activity)
from django_filters import rest_framework as django_filters



class PackageFilter(django_filters.FilterSet):
    stage = django_filters.CharFilter(field_name='stage', lookup_expr='exact')
    tour_class = django_filters.CharFilter(field_name='tour_class', lookup_expr='exact')
    state = django_filters.CharFilter(field_name='state', lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category', lookup_expr='exact')
    is_popular = django_filters.BooleanFilter(field_name='is_popular', lookup_expr='exact')

    class Meta:
        model = Package
        fields = ['tour_class', 'stage', 'state', 'category', 'is_popular']


class ActivityFilter(django_filters.FilterSet):
    stage = django_filters.CharFilter(field_name='stage', lookup_expr='exact')
    tour_class = django_filters.CharFilter(field_name='tour_class', lookup_expr='exact')
    state = django_filters.CharFilter(field_name='state', lookup_expr='exact')
    category = django_filters.CharFilter(field_name='category', lookup_expr='exact')
    is_popular = django_filters.BooleanFilter(field_name='is_popular', method='filter_is_popular')
    
    class Meta:
        model = Activity
        fields = ['tour_class', 'stage', 'state', 'category', 'is_popular']
