# serializers.py
import decimal

from api.models import UserReview
from api.v1.agent.serializers import BookingAgentSerializer
from api.v1.general.serializers import *
from api.v1.package.serializers import (BookingPackageSerializer,
                                        PackageMinFieldsSerializer)
from api.v1.user.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserReviewSerializer(serializers.ModelSerializer):
 

    class Meta:
        model = UserReview
        fields = "__all__"


class UserReviewDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(required=False)
    package = PackageMinFieldsSerializer(required=False)



    class Meta:
        model = UserReview
        fields = "__all__"