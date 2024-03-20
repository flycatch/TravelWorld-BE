from rest_framework import serializers
from api.models import Country, City, State, CoverPageInput, Attraction


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



class CoverPageInputSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CoverPageInput
        fields = ['experience','clients','satisfaction']


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
