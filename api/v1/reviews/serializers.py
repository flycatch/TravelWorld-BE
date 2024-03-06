# serializers.py
import decimal

from api.models import UserReview,UserReviewImage
from api.v1.agent.serializers import BookingAgentSerializer
from api.v1.general.serializers import *
from api.v1.package.serializers import (BookingPackageSerializer,
                                        PackageMinFieldsSerializer)
from api.v1.user.serializers import UserBookingSerializer
from api.v1.bookings.serializers import BookingMinFieldsSerializer

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReviewImage
        fields = ['id','images']


class UserReviewSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True,required=False)

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        review = UserReview.objects.create(**validated_data)
        for image_data in images_data:
            UserReviewImage.objects.create(review=review, image=image_data)
        return review


    class Meta:
        model = UserReview
        fields = "__all__"


class UserReviewDetailSerializer(serializers.ModelSerializer):
    user = UserBookingSerializer(required=False)
    package = PackageMinFieldsSerializer(required=False)
    booking = BookingMinFieldsSerializer(required=False)
    review_images = UserReviewImageSerializer(many=True,required=False)



    class Meta:
        model = UserReview
        fields = "__all__"