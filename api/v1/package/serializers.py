# serializers.py
from rest_framework import serializers
from api.models import (Package, Itinerary, ItineraryDay, Informations, Guide,
                        InformationActivities, ThingsToCarry, HotelDetails, Pricing,
                        TourCategory,CancellationPolicy, FAQQuestion, FAQAnswer)


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        exclude = ['status', 'is_submitted', 'stage']

    def create(self, validated_data):
        is_submitted = self.context['request'].data.get('is_submitted', False)

        if not is_submitted:
            return super().create(validated_data)

        validated_data['is_submitted'] = False
        instance = super().create(validated_data)
        return instance


class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        exclude = ['status']


class ItineraryDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryDay
        exclude = ['status']


class InformationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Informations
        exclude = ['status']


class HotelDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelDetails
        exclude = ['status']


class GuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        exclude = ['status']


class InformationActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformationActivities
        exclude = ['status']


class ThingsToCarrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ThingsToCarry
        exclude = ['status']


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        exclude = ['status']


class PackageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TourCategory


class PackageCancellationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationPolicy
        exclude = ['status']


class PackageFAQQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQQuestion
        exclude = ['status']


class PackageFAQAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQAnswer
        exclude = ['status']
