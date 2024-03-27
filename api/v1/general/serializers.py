from rest_framework import serializers
from api.models import Country, City, State, Location,CoverPageInput, Attraction,Pricing
from django.db.models import Max


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id','name']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id','name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id','name']


class LocationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Location
        fields = ['id', 'country', 'state', 'destinations']


class LocationGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    country = CountrySerializer(required=False)
    state = StateSerializer(required=False)
    destinations = CitySerializer(many=True,required=False)  # Include destinations

    class Meta:
        model = Location
        fields = ['id', 'country', 'state', 'destinations']


class CoverPageInputSerializer(serializers.ModelSerializer):
    price_max = serializers.SerializerMethodField()

    class Meta:
        model = CoverPageInput
        fields = ['experience','clients','satisfaction',
                  'activity_image', 'package_image', 'attraction_image','price_max','price_min']
        
    def get_price_max(self, obj):
        max_price = Pricing.objects.aggregate(max_adult_rate=Max('adults_rate'))['max_adult_rate']
        return max_price


class AttractionSerializer(serializers.ModelSerializer):
    city = CitySerializer(required=False)
    state = StateSerializer(required=False)
    class Meta:
        model = Attraction
        fields = '__all__'

class HomePageDestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'thumb_image', 'cover_img']


class HomePageStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'thumb_image', 'cover_img']
