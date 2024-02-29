from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from api.models import Country, State, City
from api.v1.general.serializers import CountrySerializer, StateSerializer, CitySerializer
from api.filters.general_filters import CityFilter


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CityFilter