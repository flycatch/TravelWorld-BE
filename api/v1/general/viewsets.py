import requests
from geopy.distance import geodesic

from django.conf import settings
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from api.models import (Country, State, City, CoverPageInput, Attraction, Location, Package,
                        Activity, Currency)
from api.v1.general.serializers import (CountrySerializer, StateSerializer, CitySerializer,
                                        AttractionSerializer, CoverPageInputSerializer,
                                        HomePageDestinationSerializer, HomePageStateSerializer,
                                        LocationSerializer, SendEnquirySerializer,
                                        CurrencySerializer)
from api.filters.general_filters import CityFilter, CurrencyFilter, StateFilter, AttractionFilter
from api.utils.paginator import CustomPagination
from api.tasks import *


class CountryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on Country objects.

    This viewset provides methods to list, create, retrieve, 
    update, and delete countries.
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class StateViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on State objects.

    This viewset provides methods to list, create, retrieve,
    update, and delete states.
    It also allows filtering states based on their associated
    country using the `StateFilter`.
    """
    queryset = State.objects.all()
    serializer_class = StateSerializer
    filterset_class = StateFilter


class CityViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on City objects.

    This viewset provides methods to list, create, retrieve,
    update, and delete cities.
    It also allows filtering cities based on their associated
    state using the `CityFilter`.
    """
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CityFilter

    def perform_create(self, serializer):
        """
        Save a new city instance after fetching its coordinates from Google Maps API.

        This method overrides the default perform_create method to include fetching
        the city's latitude and longitude from the Google Maps API based on the city name.
        The fetched coordinates are then saved with the city instance.

        Parameters:
        - serializer (CitySerializer): The serializer instance containing the validated data.
        """
        name = serializer.validated_data['name']
        lat, lng = self.get_coordinates_from_google(name)
        print(lat)
        serializer.save(latitude=lat, longitude=lng)

    def get_coordinates_from_google(self, city_name):
        """
        Fetch the latitude and longitude of a city using the Google Maps API.

        This method makes a request to the Google Maps Geocoding API to get the coordinates
        of a city based on its name.

        Parameters:
        - city_name (str): The name of the city to fetch coordinates for.

        Returns:
        - tuple: A tuple containing the latitude and longitude of the city.
        - None: If the API request fails or the city is not found, returns None.

        Raises:
        - Response: Returns an error response if there is an issue with the API request.
        """
        api_key = settings.GOOGLE_MAPS_API_KEY
        base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'address': city_name, 'key': api_key}
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            return Response({'error': 'Error fetching data from Google Maps API.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if response.status_code == 200:
            results = response.json().get('results')
            if results:
                location = results[0]['geometry']['location']
                return location['lat'], location['lng']
        return None


class CityByCoordinatesView(APIView):
    """
    API endpoint to get the city name using latitude and longitude.
    """
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to fetch the city name based on latitude and longitude.

        This method checks if both latitude and longitude are provided in the request.
        If both parameters are present, it calls the `get_city_from_coordinates` method
        to fetch the city name from the Google Maps API.

        Parameters:
        - request (Request): The request object containing query parameters.

        Returns:
        - Response: A JSON response containing the city name if found, or an error message.
        """
        lat = request.query_params.get('latitude')
        lng = request.query_params.get('longitude')
        if not lat or not lng:
            return Response({'error': 'Please provide both latitude and longitude.'},
                            status=status.HTTP_400_BAD_REQUEST)

        city = self.get_city_from_coordinates(lat, lng)
        if city:
            return Response({'city': city}, status=status.HTTP_200_OK)

        return Response({'error': 'City not found.'}, status=status.HTTP_404_NOT_FOUND)

    def get_city_from_coordinates(self, lat, lng):
        """
        Fetch the city name from the Google Maps API using latitude and longitude.

        This method makes a request to the Google Maps Geocoding API to get the city
        name based on the provided latitude and longitude.

        Parameters:
        - lat (str): The latitude of the location.
        - lng (str): The longitude of the location.

        Returns:
        - str: The name of the city if found.
        - None: If the city is not found or the API request fails.

        Raises:
        - Response: Returns an error response if there is an issue with the API request.
        """
        api_key = settings.GOOGLE_MAPS_API_KEY
        base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'latlng': f'{lat},{lng}', 'key': api_key}
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            results = response.json().get('results')
            if results:
                address_components = results[0].get('address_components')
                for component in address_components:
                    if 'locality' in component.get('types'):
                        return component.get('long_name')
        return None


class NearestCitiesAPIView(APIView):
    """
    API endpoint to get nearest cities based on latitude and longitude.
    """
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to fetch nearest cities based on latitude and longitude.

        This method checks if both latitude and longitude are provided in the request.
        It also takes an optional `max_distance` parameter to limit the search radius.
        If the parameters are valid, it calls the `get_nearest_cities` method to get
        the nearest cities.

        Parameters:
        - request (Request): The request object containing query parameters.

        Returns:
        - Response: A JSON response containing the list of nearest city names if found,
                    or an error message.
        """
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        max_distance = request.query_params.get('max_distance', 100)  # Default max distance is 100 km

        if not latitude or not longitude:
            return Response({'error': 'Please provide both latitude and longitude.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            max_distance = float(max_distance)
        except ValueError:
            return Response({'error': 'Invalid latitude, longitude, or max_distance values.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get nearest cities based on coordinates
        nearest_cities = self.get_nearest_cities(latitude, longitude, max_distance)

        if not nearest_cities:
            return Response({'message': 'No cities found within the specified distance.'},
                            status=status.HTTP_404_NOT_FOUND)

        # Extract city names from queryset
        city_names = [city.name for city in nearest_cities]

        return Response({'nearest_cities': city_names}, status=status.HTTP_200_OK)

    def get_nearest_cities(self, latitude, longitude, max_distance=100):
        """
        Retrieve nearest cities based on given latitude and longitude.

        This method calculates the distance between the given coordinates and the
        coordinates of each city in the database. It filters the cities within the
        specified maximum distance and returns them sorted by distance.

        Parameters:
        - latitude (float): Latitude of the reference point (in degrees).
        - longitude (float): Longitude of the reference point (in degrees).
        - max_distance (float): Maximum distance (in kilometers) to search for cities.

        Returns:
        - list: A list of City objects ordered by distance.
        """
        origin = (latitude, longitude)
        cities = City.objects.all()

        nearby_cities = []
        for city in cities:
            if city.latitude is not None and city.longitude is not None:
                destination = (city.latitude, city.longitude)
                distance = geodesic(origin, destination).km
                if distance <= max_distance:
                    city.distance = distance
                    nearby_cities.append(city)

        # Sort cities by distance
        nearby_cities.sort(key=lambda city: city.distance)
        return nearby_cities


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
                'statusCode': status.HTTP_200_OK},
                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e), 'status': 'error'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CoverPageView(APIView):
    
    serializer_class = CoverPageInputSerializer


    def get(self, request, *args, **kwargs):
        try:
            
            queryset = CoverPageInput.objects.all()
            serializer = self.serializer_class(queryset, many=True, context={'request':request})
            return Response({"results":serializer.data,
                            "message":"Listed successfully",
                            "status": "success",
                            "statusCode": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    
        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttractionView(ListAPIView):
    serializer_class = AttractionSerializer
    pagination_class = CustomPagination
    filterset_class = AttractionFilter

    def get_queryset(self):
        queryset = Attraction.objects.order_by("-id")
        return queryset
        
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as error_message:
            response_data = {
                "message": f"Something went wrong: {error_message}",
                "status": "error",
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HomePageDestinationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for fetching active cities for the home page.

    This viewset provides a list of active cities with support for pagination
    and filtering based on various criteria.

    Attributes:
        queryset (QuerySet): The base queryset of active cities.
        serializer_class (Serializer): The serializer class for transforming city data.
        pagination_class (Pagination): The pagination class used for paginating results.
        filter_backends (list): The filter backends used for filtering and searching.
        filterset_class (FilterSet): The filter set class used for filtering city data.
    """
    queryset = City.objects.filter(status='active')
    serializer_class = HomePageDestinationSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = CityFilter


class HomePageStateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for fetching active states for the home page.

    This viewset provides a list of active states with support for pagination
    and filtering based on various criteria.

    Attributes:
        queryset (QuerySet): The base queryset of active states.
        serializer_class (Serializer): The serializer class for transforming state data.
        pagination_class (Pagination): The pagination class used for paginating results.
        filter_backends (list): The filter backends used for filtering and searching.
        filterset_class (FilterSet): The filter set class used for filtering state data.
    """
    queryset = State.objects.filter(status='active')
    serializer_class = HomePageStateSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = StateFilter


class SendEnquiryView(APIView):
    
    serializer_class = SendEnquirySerializer

   
    def post(self, request, *args, **kwargs):
        try:

            with transaction.atomic():

                if 'package' in request.data:
                        instance = Package.objects.get(id=request.data['package'])
                        product_uid = instance.package_uid
                else:
                        instance = Activity.objects.get(id=request.data['activity'])
                        product_uid = instance.activity_uid

                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    serializer.save()

                    send_enquiry_email.delay(
                        "Explore World | New Enquiry",
                        'email/custom_email_template.html',
                        instance.agent.email,
                        {'data': {
                            'name': request.data['name'],
                            'email': request.data['email'],
                            'contact_number': request.data['country_code'] + request.data['contact_number'],
                            'message': request.data['message'],
                            'product_id': product_uid,
                            'product_title': instance.title,
                            }
                        },
                    )

                    return Response({"message":"Enquiry send successfully",
                                "status": "success",
                                "statusCode": status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
                
                else:
                    return Response({ "message": f"Something went wrong : {serializer.errors}",
                                    "status": "error",
                                    "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for retrieving and filtering currency data.

    Provides read-only access to a list of currencies, allowing for filtering
    by specific criteria defined in the `CurrencyFilter` class. Supports
    custom pagination through the `CustomPagination` class.

    Relationships:
        - Related to the `Currency` model and `CurrencySerializer`.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CurrencyFilter
    pagination_class = CustomPagination
