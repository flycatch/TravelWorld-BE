# serializers.py
import decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import (Package, Itinerary, ItineraryDay, Informations, Pricing,
                        TourCategory,CancellationPolicy, FAQQuestion, FAQAnswer,
                        PackageImage, PackageCategory)


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        exclude = ['status', 'is_submitted', 'stage']

    # def validate_min_members(self, value):
    #     if value < 1:
    #         raise serializers.ValidationError("Minimum number of members must be at least 1.")
    #     return value

    # def validate_max_members(self, value):
    #     if value < 1:
    #         raise serializers.ValidationError("Maximum number of members must be at least 1.")
    #     return value

    def create(self, validated_data):
        try:
            is_submitted = self.context['request'].data.get('is_submitted', False)

            if not is_submitted:
                return super().create(validated_data)

            validated_data['is_submitted'] = False
            instance = super().create(validated_data)
            return instance
        except Exception as e:
            raise ValidationError("Error creating package: {}".format(str(e)))


class PackageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImage
        exclude = ['status']


# class PackageTourTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TourType
#         exclude = ['status']


class ItineraryDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryDay
        exclude = ['status']


class ItinerarySerializer(serializers.ModelSerializer):
    itinerary_day = ItineraryDaySerializer(many=True)

    class Meta:
        model = Itinerary
        exclude = ['status']

    def create(self, validated_data):
        itinerary_day_data = validated_data.pop('itinerary_day')
        inclusions_data = validated_data.pop('inclusions', [])
        exclusions_data = validated_data.pop('exclusions', [])

        try:
            itinerary = Itinerary.objects.create(**validated_data)

            for day_data in itinerary_day_data:
                try:
                    itinerary_day_obj = ItineraryDay.objects.create(**day_data)
                    itinerary.itinerary_day.add(itinerary_day_obj)
                except Exception as error:
                    # Rollback the transaction if an exception occurs
                    itinerary.delete()
                    raise ValidationError(f"Error creating ItineraryDay: {error}")

            itinerary.inclusions.set(inclusions_data)
            itinerary.exclusions.set(exclusions_data)
        except Exception as error:
            raise ValidationError(f"Error creating Itinerary: {error}")

        return itinerary


class InformationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Informations
        exclude = ['status']


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        exclude = ['status']

    def validate_group_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Group rate cannot be negative.")
        return value

    def validate_group_commission(self, value):
        if value < 0:
            raise serializers.ValidationError("Group commission cannot be negative.")
        return value

    def validate_adult_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Adult rate cannot be negative.")
        return value

    def validate_adult_commission(self, value):
        if value < 0:
            raise serializers.ValidationError("Adult commission cannot be negative.")
        return value

    def validate_child_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Child rate cannot be negative.")
        return value

    def validate_child_commission(self, value):
        if value < 0:
            raise serializers.ValidationError("Child commission cannot be negative.")
        return value

    def validate_infant_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Infant rate cannot be negative.")
        return value

    def validate_infant_commission(self, value):
        if value < 0:
            raise serializers.ValidationError("Infant commission cannot be negative.")
        return value
        
    def validate(self, data):
        # Ensure that group_commission <= group_rate
        group_rate = data.get('group_rate')
        group_commission = data.get('group_commission')
        if group_rate is not None and group_commission is not None and group_commission > group_rate:
            raise serializers.ValidationError("Group commission cannot be greater than group rate.")

        # Ensure that adult_commission <= adult_rate
        adult_rate = data.get('adult_rate')
        adult_commission = data.get('adult_commission')
        if adult_rate is not None and adult_commission is not None and adult_commission > adult_rate:
            raise serializers.ValidationError("Adult commission cannot be greater than adult rate.")

        # Ensure that child_commission <= child_rate
        child_rate = data.get('child_rate')
        child_commission = data.get('child_commission')
        if child_rate is not None and child_commission is not None and child_commission > child_rate:
            raise serializers.ValidationError("Child commission cannot be greater than child rate.")

        # Ensure that infant_commission <= infant_rate
        infant_rate = data.get('infant_rate')
        infant_commission = data.get('infant_commission')
        if infant_rate is not None and infant_commission is not None and infant_commission > infant_rate:
            raise serializers.ValidationError("Infant commission cannot be greater than infant rate.")

        return data


class PackageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageCategory
        fields = ['id', 'name']



class PackageTourCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TourCategory
        exclude = ['status']

    def validate(self, data):
        category_type = data.get('type')
        start_at = data.get('start_at')
        end_at = data.get('end_at')

        if category_type == 'seasonal':
            if not start_at or not end_at:
                raise serializers.ValidationError("Start date and end date are required for seasonal category type.")
            if start_at >= end_at:
                raise serializers.ValidationError("Start date must be before end date for seasonal category type.")

        return data


class PackageCancellationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationPolicy
        exclude = ['status']

    def validate_amount_percent(self, value):
        # Validate that the amount_percent is a valid decimal value between 0 and 100
        try:
            percent = decimal.Decimal(value)
            if percent < 0 or percent > 100:
                raise serializers.ValidationError("Amount percent must be between 0 and 100.")
        except decimal.InvalidOperation:
            raise serializers.ValidationError("Amount percent must be a valid decimal value.")
        
        return value



class PackageFAQQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQQuestion
        exclude = ['status']


class PackageFAQAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQAnswer
        exclude = ['status']



class BookingPackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Package
        exclude = ['status', 'is_submitted', 'stage']