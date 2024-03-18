from rest_framework import serializers
from api.models import Country, City, State, Location


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
    destinations = CitySerializer(many=True)  # Include destinations

    class Meta:
        model = Location
        fields = ['id', 'country', 'state', 'destinations']