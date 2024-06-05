from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,status
from rest_framework.filters import SearchFilter

from api.models import (Country, State, City, CoverPageInput,Attraction, Location,Package,
                        Activity, Currency)
from api.v1.general.serializers import (CountrySerializer, StateSerializer, CitySerializer, 
                                        AttractionSerializer,CoverPageInputSerializer,
                                        HomePageDestinationSerializer, HomePageStateSerializer,
                                        LocationSerializer, SendEnquirySerializer, CurrencySerializer)
from api.filters.general_filters import CityFilter, CurrencyFilter, StateFilter, AttractionFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from api.utils.paginator import CustomPagination
from django.db import transaction
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
