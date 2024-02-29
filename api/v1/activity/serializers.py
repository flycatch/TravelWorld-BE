# serializers.py
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import (Activity, ActivityItinerary, ActivityItineraryDay, ActivityInformations, ActivityPricing,
                        ActivityTourCategory,ActivityCancellationPolicy, ActivityFaqCategory, ActivityFaqQuestionAnswer,
                        ActivityImage, PackageCategory, Inclusions, Exclusions,
                        ActivityInclusionInformation, ActivityExclusionInformation, ActivityCancellationCategory)
from api.v1.agent.serializers import BookingAgentSerializer
from api.v1.general.serializers import *



class ActivitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    agent_name = serializers.CharField(source='agent.agent_uid', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = Activity
        exclude = ['status', 'is_submitted']

    def validate(self, data):
        min_members = data.get('min_members')
        max_members = data.get('max_members')

        try:
            if min_members is not None and max_members is not None:
                if min_members >= max_members:
                    raise ValidationError("The 'min_members' must be less than 'max_members'.")
        except ValueError:
            raise ValidationError("Invalid value, Must be a number.")

        return data

    def create(self, validated_data):
        try:
            is_submitted = self.context['request'].data.get('is_submitted', False)

            if not is_submitted:
                return super().create(validated_data)

            validated_data['is_submitted'] = False
            instance = super().create(validated_data)
            return instance
        
        except Exception as error:
            raise ValidationError("Error creating Activity: {}".format(str(error)))


class ActivityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityImage
        exclude = ['status', 'created_on', 'updated_on',]


class ActivityItineraryDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityItineraryDay
        exclude = ['status', 'created_on', 'updated_on']


class ActivityItinerarySerializer(serializers.ModelSerializer):
    itinerary_day = ActivityItineraryDaySerializer(many=True)

    class Meta:
        model = ActivityItinerary
        exclude = ['status', 'created_on', 'updated_on']

    def create(self, validated_data):
        itinerary_day_data = validated_data.pop('itinerary_day')
        inclusions_data = validated_data.pop('inclusions', [])
        exclusions_data = validated_data.pop('exclusions', [])

        try:
            itinerary = ActivityItinerary.objects.create(**validated_data)

            for day_data in itinerary_day_data:
                try:
                    itinerary_day_obj = ActivityItineraryDay.objects.create(**day_data)
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


class ActivityInclusionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inclusions
        fields = ['id', 'name']


class ActivityExclusionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exclusions
        fields = ['id', 'name']


class ActivityInclusionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityInclusionInformation
        fields = ['inclusion', 'details',]


class ActivityExclusionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityExclusionInformation
        fields = ['exclusion', 'details',]


class ActivityInformationsSerializer(serializers.ModelSerializer):
    inclusiondetails = ActivityInclusionInformationSerializer(many=True, required=False)
    exclusiondetails = ActivityExclusionInformationSerializer(many=True, required=False)
    class Meta:
        model = ActivityInformations
        exclude = ['status', 'created_on', 'updated_on',]

    def create(self, validated_data):
        inclusion_details_data = validated_data.pop('inclusiondetails', None)
        exclusion_details_data = validated_data.pop('exclusiondetails', None)

        try:
            activity_informations = ActivityInformations.objects.create(**validated_data)

            if inclusion_details_data:
                for inclusion_data in inclusion_details_data:
                    inclusion_details_obj = ActivityInclusionInformation.objects.create(**inclusion_data)
                    activity_informations.inclusiondetails.add(inclusion_details_obj)

            if exclusion_details_data:
                for exclusion_data in exclusion_details_data:
                    exclusion_details_obj = ActivityExclusionInformation.objects.create(**exclusion_data)
                    activity_informations.exclusiondetails.add(exclusion_details_obj)

            activity_informations.save()

        except Exception as error:
            raise ValidationError(f"Error creating ActivityInformations: {error}")

        return activity_informations


class ActivityPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPricing
        exclude = ['status', 'created_on', 'updated_on',]

    def validate_group_rate(self, value):
        if value < 0:
            raise ValidationError("Group rate cannot be negative.")
        return value

    def validate_group_commission(self, value):
        if value < 0:
            raise ValidationError("Group commission cannot be negative.")
        return value

    def validate_adult_rate(self, value):
        if value < 0:
            raise ValidationError("Adult rate cannot be negative.")
        return value

    def validate_adult_commission(self, value):
        if value < 0:
            raise ValidationError("Adult commission cannot be negative.")
        return value

    def validate_child_rate(self, value):
        if value < 0:
            raise ValidationError("Child rate cannot be negative.")
        return value

    def validate_child_commission(self, value):
        if value < 0:
            raise ValidationError("Child commission cannot be negative.")
        return value

    def validate_infant_rate(self, value):
        if value < 0:
            raise ValidationError("Infant rate cannot be negative.")
        return value

    def validate_infant_commission(self, value):
        if value < 0:
            raise ValidationError("Infant commission cannot be negative.")
        return value
        
    def validate(self, data):
        # Ensure that group_commission <= group_rate
        group_rate = data.get('group_rate')
        group_commission = data.get('group_commission')
        if group_rate is not None and group_commission is not None and group_commission > group_rate:
            raise ValidationError("Group commission cannot be greater than group rate.")

        # Ensure that adult_commission <= adult_rate
        adult_rate = data.get('adult_rate')
        adult_commission = data.get('adult_commission')
        if adult_rate is not None and adult_commission is not None and adult_commission > adult_rate:
            raise ValidationError("Adult commission cannot be greater than adult rate.")

        # Ensure that child_commission <= child_rate
        child_rate = data.get('child_rate')
        child_commission = data.get('child_commission')
        if child_rate is not None and child_commission is not None and child_commission > child_rate:
            raise ValidationError("Child commission cannot be greater than child rate.")

        # Ensure that infant_commission <= infant_rate
        infant_rate = data.get('infant_rate')
        infant_commission = data.get('infant_commission')
        if infant_rate is not None and infant_commission is not None and infant_commission > infant_rate:
            raise ValidationError("Infant commission cannot be greater than infant rate.")

        return data


class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageCategory
        fields = ['id', 'name']



class ActivityTourCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTourCategory
        exclude = ['status', 'created_on', 'updated_on',]

    def validate(self, data):
        category_type = data.get('type')
        start_at = data.get('start_at')
        end_at = data.get('end_at')

        if category_type == 'seasonal':
            if not start_at or not end_at:
                raise ValidationError("Start date and end date are required for seasonal category type.")
            if start_at >= end_at:
                raise ValidationError("Start date must be before end date for seasonal category type.")

        return data


class ActivityCancellationPolicyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCancellationCategory
        fields = ['from_day', 'to_day', 'amount_percent',]


class ActivityCancellationPolicySerializer(serializers.ModelSerializer):
    category = ActivityCancellationPolicyCategorySerializer(many=True, required=False)

    class Meta:
        model = ActivityCancellationPolicy
        exclude = ['status', 'created_on', 'updated_on',]

    def create(self, validated_data):
        category_data = validated_data.pop('category', [])

        try:
            cancellation_policy = ActivityCancellationPolicy.objects.create(**validated_data)

            for data in category_data:
                print(data)
                cancellation_category_data = ActivityCancellationCategory.objects.create(**data)
                cancellation_policy.category.add(cancellation_category_data)

        except Exception as error:
            raise serializers.ValidationError(f"Error creating Cancellation Policy: {error}")

        return cancellation_policy


class ActivityFaqCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityFaqCategory
        fields = ['question', 'answer',]


class ActivityFaqQuestionAnswerSerializer(serializers.ModelSerializer):
    category = ActivityFaqCategorySerializer(many=True, required=False)
    class Meta:
        model = ActivityFaqQuestionAnswer
        exclude = ['status', 'created_on', 'updated_on',]

    def create(self, validated_data):
        category_data = validated_data.pop('category', [])

        try:
            activity_faq_data = ActivityFaqQuestionAnswer.objects.create(**validated_data)

            for data in category_data:
                print(data)
                faq_category_data = ActivityFaqCategory.objects.create(**data)
                activity_faq_data.category.add(faq_category_data)
        except Exception as error:
            raise serializers.ValidationError(f"Error creating Activity FAQ: {error}")

        return activity_faq_data


class ActivityBookingSerializer(serializers.ModelSerializer):
    agent = BookingAgentSerializer(required=False)
    city = CitySerializer(required=False)
    state = StateSerializer(required=False)
    country = CountrySerializer(required=False)

    class Meta:
        model = Activity
        fields = ["id","activity_uid","title","tour_class",
                  "country","state","city","agent"]
        

class ActivityMinFieldsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Activity
        fields = ['id','activity_uid','title']