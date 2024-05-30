"""
API filters for models in the `api` app.

This module defines filters for the `City`, `State`, and `Currency`
models used in the `api` app.
These filters allow for searching and filtering objects based on related
models through foreign keyrelationships.

- **CustomBooleanFilter:** Filters by true,1 or false,0 value.
- **CityFilter:** Filters cities based on the ID of their associated state.
- **StateFilter:** Filters states based on the ID of their associated country.
- **CurrencyFilter:** Filters currencies based on the ID of their associated country.
"""
import django_filters
from django_filters import rest_framework as filters

from api.models import City, State, Currency, Attraction


class CustomBooleanFilter(filters.BooleanFilter):
    """
    Custom filter to handle different string representations of boolean values.

    This filter interprets various string values as boolean True or False. Specifically,
    it treats the following string values as True: '1', 'true'. It treats the following
    string values as False: '0', 'false'. This allows for more flexible URL parameters
    when filtering boolean fields.

    Methods:
        filter(qs, value): Filters the queryset based on the interpreted boolean value.
            - qs: The initial queryset to filter.
            - value: The value to interpret as a boolean.

    Returns:
        Filtered queryset based on the interpreted boolean value.
    """
    def filter(self, qs, value):
        if value in (None, ''):
            return qs
        if isinstance(value, str):
            value = value.lower()
            if value in ('1', 'true'):
                value = True
            elif value in ('0', 'false'):
                value = False
            else:
                return qs
        return super().filter(qs, value)


class CityFilter(django_filters.FilterSet):
    """
    Filter for City objects based on their state and popular.
    This filter allows filtering cities based on the ID of their associated state.

    **Fields:**
    * state (CharFilter): Filters cities by the ID of their state.
    * is_popular (CustomBooleanFilter): Filters is_popular by true or false value.
    """
    state = django_filters.CharFilter(field_name='state__id')
    is_popular = CustomBooleanFilter(field_name='is_popular', lookup_expr='exact')

    class Meta:
        """
        Meta options for AttractionFilter.

        **Attributes:**
        * model (api.models): The model that this filter set is based on.
        * fields (list): The list of fields that this filter set can filter on.
        """
        model = City
        fields = ['state', 'is_popular']


class StateFilter(django_filters.FilterSet):
    """
    Filter for State objects based on their country and popular.
    This filter allows filtering states based on the ID of their associated country.

    **Fields:**
    * country (CharFilter): Filters states by the ID of their country.
    * is_popular (CustomBooleanFilter): Filters is_popular by true or false value.
    """
    country = django_filters.CharFilter(field_name='country__id')
    is_popular = CustomBooleanFilter(field_name='is_popular', lookup_expr='exact')

    class Meta:
        """
        Meta options for AttractionFilter.

        **Attributes:**
        * model (api.models): The model that this filter set is based on.
        * fields (list): The list of fields that this filter set can filter on.
        """
        model = State
        fields = ['country', 'is_popular']


class CurrencyFilter(django_filters.FilterSet):
    """
    Filter for the `Currency` model by country.
    Allows filtering currencies based on their associated country ID.
    Fields:
        country: Filters currencies by country ID (lookup field: 'country__id').
    """
    country = django_filters.CharFilter(field_name='country__id')

    class Meta:
        """
        Meta options for AttractionFilter.

        **Attributes:**
        * model (api.models): The model that this filter set is based on.
        * fields (list): The list of fields that this filter set can filter on.
        """
        model = Currency
        fields = ['country']


class AttractionFilter(django_filters.FilterSet):
    """
    Filter for Attraction objects based on their state.
    This filter allows filtering Attraction based on the ID of their associated state.

    **Fields:**
    * state (CharFilter): Filters cities by the ID of their state.
    """
    state = django_filters.CharFilter(field_name='state__id')

    class Meta:
        """
        Meta options for AttractionFilter.

        **Attributes:**
        * model (api.models): The model that this filter set is based on.
        * fields (list): The list of fields that this filter set can filter on.
        """
        model = Attraction
        fields = ['state']
