from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from api.models import Country, State, City, Location
from api.v1.general.serializers import CountrySerializer, StateSerializer, CitySerializer, LocationSerializer
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


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    http_method_names = ['get', 'delete']

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({
                'message': 'Location deleted successfully', 'status': 'success', 
                'statusCode': status.HTTP_204_NO_CONTENT},
                status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': str(e), 'status': 'error'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)