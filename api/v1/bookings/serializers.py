import decimal

from api.models import (Booking, CancellationPolicy, FAQAnswer, FAQQuestion,
                        PackageInformations, Itinerary, ItineraryDay, Package,
                        PackageImage, Pricing, TourCategory)
from rest_framework import serializers
from api.v1.package.serializers import BookingPackageSerializer


class BookingSerializer(serializers.ModelSerializer):
    package = BookingPackageSerializer(required=False)

    class Meta:
        model = Booking
        fields = "__all__"
        