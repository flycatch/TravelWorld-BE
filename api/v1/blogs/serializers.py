import decimal

from api.models import *
from rest_framework import serializers
from api.v1.package.serializers import BookingPackageSerializer
from api.v1.user.serializers import UserBookingSerializer
from api.v1.agent.serializers import BookingAgentSerializer
from api.v1.activity.serializers import BookingActivitySerializer


class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['id','image']

class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id','name']


class BlogSerializer(serializers.ModelSerializer):
    blogs_image = BlogImageSerializer(many=True,required=False)
    categories = BlogCategorySerializer(many=True,required=False)

    class Meta:
        model = Blogs
        fields = "__all__"