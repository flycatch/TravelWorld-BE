from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,status
from django.db.models import Count
from django.utils import timezone

from api.models import Country, State, City, CoverPageInput,Attraction, Location,Package,Activity,Booking
from api.v1.general.serializers import (CountrySerializer, StateSerializer, CitySerializer, 
                                        AttractionSerializer,CoverPageInputSerializer,
                                        HomePageDestinationSerializer, HomePageStateSerializer, LocationSerializer,
                                        SendEnquirySerializer)
from api.filters.general_filters import CityFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from api.utils.paginator import CustomPagination
from django.db import transaction
from api.tasks import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class DashboardCount(APIView):
  
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
      
        try:
            current_date = timezone.now().date()
            deal_type = self.request.GET.get("deal_type")

            if deal_type == 'PACKAGE':

                # Retrieve successful bookings count for past, ongoing, and future bookings
                past_successful_bookings_count = Booking.objects.filter(
                booking_status='SUCCESSFUL',
                tour_date__lt=current_date,
                package__agent=request.user,
                package__isnull=False
                ).count()

                ongoing_successful_bookings_count = Booking.objects.filter(
                    booking_status='SUCCESSFUL',
                    tour_date=current_date,
                    package__agent=request.user,
                    package__isnull=False
                ).count()

                future_successful_bookings_count = Booking.objects.filter(
                    booking_status='SUCCESSFUL',
                    tour_date__gt=current_date,
                    package__agent=request.user,
                    package__isnull=False
                ).count()

            elif deal_type == 'ACTIVITY':

                # Retrieve successful bookings count for past, ongoing, and future bookings
                past_successful_bookings_count = Booking.objects.filter(
                booking_status='SUCCESSFUL',
                tour_date__lt=current_date,
                activity__agent=request.user,
                activity__isnull=False
                ).count()

                ongoing_successful_bookings_count = Booking.objects.filter(
                    booking_status='SUCCESSFUL',
                    tour_date=current_date,
                    activity__agent=request.user,
                    activity__isnull=False
                ).count()

                future_successful_bookings_count = Booking.objects.filter(
                    booking_status='SUCCESSFUL',
                    tour_date__gt=current_date,
                    activity__agent=request.user,
                    activity__isnull=False
                ).count()

            results ={
                "past_successful_bookings_count" :past_successful_bookings_count,
                "ongoing_successful_bookings_count":ongoing_successful_bookings_count,
                "future_successful_bookings_count":future_successful_bookings_count
            }

            return Response({
                    "status": "success",
                    "message": "Listed successfully",
                    "statusCode": status.HTTP_200_OK,
                    "results": results
                }, status=status.HTTP_200_OK)

        except Exception as exception:
            return Response({'message': str(exception)}, status=status.HTTP_400_BAD_REQUEST)