import decimal

from api.models import (Booking, CancellationPolicy, FAQAnswer, FAQQuestion,
                        PackageInformations, Itinerary, ItineraryDay, Package,
                        PackageImage, Pricing, TourCategory)
from rest_framework import serializers
from api.v1.package.serializers import BookingPackageSerializer
from api.v1.user.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    package = BookingPackageSerializer(required=False)
    user = UserSerializer(required=False)

    class Meta:
        model = Booking
        fields = "__all__"
        