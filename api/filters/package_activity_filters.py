from api.models import (Package,Activity)
from django_filters import rest_framework as django_filters



class PackageFilter(django_filters.FilterSet):
    stage = django_filters.CharFilter(field_name='stage', lookup_expr='exact')
    tour_class = django_filters.CharFilter(field_name='tour_class', lookup_expr='exact')


    class Meta:
        model = Package
        fields = ['tour_class', 'stage']


class ActivityFilter(django_filters.FilterSet):
    stage = django_filters.CharFilter(field_name='stage', lookup_expr='exact')
    tour_class = django_filters.CharFilter(field_name='tour_class', lookup_expr='exact')


    class Meta:
        model = Activity
        fields = ['tour_class', 'stage']