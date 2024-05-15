import django_filters
from api.models import City, Currency


class CityFilter(django_filters.FilterSet):
    state = django_filters.CharFilter(field_name='state__id')

    class Meta:
        model = City
        fields = ['state']


class CurrencyFilter(django_filters.FilterSet):
    """
    Filter for the `Currency` model by country.
    Allows filtering currencies based on their associated country ID.
    Fields:
        country: Filters currencies by country ID (lookup field: 'country__id').
    """
    country = django_filters.CharFilter(field_name='country__id')

    class Meta:
        model = Currency
        fields = ['country']