from rest_framework import serializers
from api.models import Country, City, State, CoverPageInput


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