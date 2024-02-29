import django_filters
from api.models import City


class CityFilter(django_filters.FilterSet):
    state = django_filters.CharFilter(field_name='state__id')

    class Meta:
        model = City
        fields = ['state']