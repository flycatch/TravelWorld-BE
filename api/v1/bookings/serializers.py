import decimal

from api.models import *
from rest_framework import serializers
from api.v1.package.serializers import BookingPackageSerializer
from api.v1.user.serializers import UserBookingSerializer
from api.v1.agent.serializers import BookingAgentSerializer



class ContactPersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactPerson
        fields = "__all__"


class BookingUserReviewSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True,required=False)

    class Meta:
        model = UserReview
        fields = "__all__"

class BookingSerializer(serializers.ModelSerializer):
    package = BookingPackageSerializer(required=False)
    user = UserBookingSerializer(required=False)
    contact_person_booking = ContactPersonSerializer(many=True, read_only=True)
    user_review_booking = BookingUserReviewSerializer(required=False)

    class Meta:
        model = Booking
        fields = "__all__"

class BookingCreateSerializer(serializers.ModelSerializer):
 

    class Meta:
        model = Booking
        fields = "__all__"
        

class BookingMinFieldsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Booking
        fields = ['id','booking_id']


class AgentTransactionSettlementSerializer(serializers.ModelSerializer):
 

    class Meta:
        model = AgentTransactionSettlement
        fields = "__all__"
        


class AgentTransactionSettlementDetailSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(required=False)

    class Meta:
        model = AgentTransactionSettlement
        fields = "__all__"
