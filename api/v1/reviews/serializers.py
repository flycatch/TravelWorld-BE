# serializers.py
import decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import (UserReview)
from api.v1.agent.serializers import BookingAgentSerializer
from api.v1.general.serializers import *


class UserReviewSerializer(serializers.ModelSerializer):
 

    class Meta:
        model = UserReview
        fields = "__all__"