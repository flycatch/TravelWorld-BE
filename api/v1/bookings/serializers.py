import decimal

from api.models import (Booking, CancellationPolicy, FAQAnswer, FAQQuestion,
                        Informations, Itinerary, ItineraryDay, Package,
                        PackageImage, Pricing, TourCategory)
from rest_framework import serializers


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        