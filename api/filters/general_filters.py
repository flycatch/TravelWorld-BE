"""
API filters for models in the `api` app.

This module defines filters for the `City`, `State`, and `Currency` models used in the `api` app.
These filters allow for searching and filtering objects based on related models through foreign key relationships.

- **CityFilter:** Filters cities based on the ID of their associated state.
- **StateFilter:** Filters states based on the ID of their associated country.
- **CurrencyFilter:** Filters currencies based on the ID of their associated country.
"""
import django_filters
from api.models import City, State, Currency


class CityFilter(django_filters.FilterSet):
    """
    Filter for City objects based on their state.
    This filter allows filtering cities based on the ID of their associated state.

    **Fields:**
    * state (CharFilter): Filters cities by the ID of their state.
    """
    state = django_filters.CharFilter(field_name='state__id')

    class Meta:
        model = City
        fields = ['state']


class StateFilter(django_filters.FilterSet):
    """
    Filter for State objects based on their country.
    This filter allows filtering states based on the ID of their associated country.

    **Fields:**
    * country (CharFilter): Filters states by the ID of their country.
    """
    country = django_filters.CharFilter(field_name='country__id')

    class Meta:
        model = State
        fields = ['country']


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