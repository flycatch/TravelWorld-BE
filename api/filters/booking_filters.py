from api.models import (Booking, CancellationPolicy, FAQAnswer, FAQQuestion,
                        Informations, Itinerary, ItineraryDay, Package,
                        PackageImage, Pricing, TourCategory)
from django_filters import rest_framework as django_filters



class BookingFilter(django_filters.FilterSet):
    booking_status = django_filters.CharFilter(field_name='booking_status', lookup_expr='exact')

    class Meta:
        model = Booking
        fields = ['booking_status', 'check_in']
