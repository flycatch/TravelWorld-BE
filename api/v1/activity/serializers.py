# serializers.py
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from api.models import (Activity, ActivityItinerary, ActivityInformations, ActivityPricing,
                        ActivityTourCategory,ActivityCancellationPolicy, ActivityFaqCategory, ActivityFaqQuestionAnswer,
                        ActivityImage, PackageCategory, Inclusions, Exclusions, Location,
                        ActivityInclusionInformation, ActivityExclusionInformation, ActivityCancellationCategory)
from api.v1.agent.serializers import BookingAgentSerializer
from api.v1.general.serializers import *
from django.db.models import Avg


class ActivitySerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.agent_uid', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    locations = LocationSerializer(many=True)

    class Meta:
        model = Activity
        exclude = ['status', 'is_submitted', 'is_popular', "deal_type"]

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

    @transaction.atomic
    def create(self, validated_data):
        locations_data = validated_data.pop('locations', [])

        activity = Activity.objects.create(**validated_data)

        for location_data in locations_data:
            try:
                destination_ids = location_data.pop('destinations', [])
                locations_obj = Location.objects.create(**location_data)
                locations_obj.destinations.set(destination_ids)
                activity.locations.add(locations_obj)

            except Exception as error:
                raise serializers.ValidationError(error)

        return activity

    def update(self, instance, validated_data):
        locations_data = validated_data.pop('locations', [])

        # Update or create related locations
        for location_data in locations_data:
            location_id = location_data.get('id')
            if location_id:
                try:
                    location_obj = Location.objects.get(pk=location_id)
                    LocationSerializer().update(instance=location_obj, validated_data=location_data)
                except Location.DoesNotExist:
                    raise serializers.ValidationError(f"Location with id {location_id} does not exist.")
            else:
                destination_ids = location_data.pop('destinations', [])
                locations_obj = Location.objects.create(**location_data)
                locations_obj.destinations.set(destination_ids)
                instance.locations.add(locations_obj)

        return super().update(instance, validated_data)


class ActivityImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityImage
        exclude = ['status', 'created_on', 'updated_on',]


class ActivityItinerarySerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityItinerary
        exclude = ['status', 'created_on', 'updated_on']

    def create(self, validated_data):
        inclusions_data = validated_data.pop('inclusions', [])
        exclusions_data = validated_data.pop('exclusions', [])

        try:
            itinerary = ActivityItinerary.objects.create(**validated_data)
            itinerary.inclusions.set(inclusions_data)
            itinerary.exclusions.set(exclusions_data)
        except Exception as error:
            raise ValidationError(f"Error creating Itinerary: {error}")

        return itinerary

    def update(self, instance, validated_data):
        inclusions_data = validated_data.pop('inclusions', None)
        exclusions_data = validated_data.pop('exclusions', None)

        # Update the main Itinerary instance
        instance.overview = validated_data.get('overview', instance.overview)
        instance.important_message = validated_data.get('important_message', instance.important_message)
        instance.things_to_carry = validated_data.get('things_to_carry', instance.things_to_carry)

        # Update inclusions if data provided
        if inclusions_data is not None:
            instance.inclusions.set(inclusions_data)

        # Update exclusions if data provided
        if exclusions_data is not None:
            instance.exclusions.set(exclusions_data)

        instance.save()
        return instance


class ActivityInclusionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inclusions
        fields = ['id', 'name']


class ActivityExclusionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exclusions
        fields = ['id', 'name']


class ActivityInclusionInformationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(source='inclusion.name', read_only=True, required=False)

    # inclusion = serializers.PrimaryKeyRelatedField(queryset=Inclusions.objects.all(), required=False)

    class Meta:
        model = ActivityInclusionInformation
        fields = ['id', 'inclusion', 'name', 'details',]


class ActivityExclusionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityExclusionInformation
        fields = ['id', 'exclusion', 'details',]


class ActivityInformationsSerializer(serializers.ModelSerializer):
    inclusiondetails = ActivityInclusionInformationSerializer(many=True, required=False)

    class Meta:
        model = ActivityInformations
        exclude = ['status', 'created_on', 'updated_on',]

    def create(self, validated_data):
        inclusion_details_data = validated_data.pop('inclusiondetails', None)
        # exclusion_details_data = validated_data.pop('exclusiondetails', None)

        try:
            activity_informations = ActivityInformations.objects.create(**validated_data)

            if inclusion_details_data:
                for inclusion_data in inclusion_details_data:
                    inclusion_details_obj = ActivityInclusionInformation.objects.create(**inclusion_data)
                    activity_informations.inclusiondetails.add(inclusion_details_obj)

            # if exclusion_details_data:
            #     for exclusion_data in exclusion_details_data:
            #         exclusion_details_obj = ActivityExclusionInformation.objects.create(**exclusion_data)
            #         activity_informations.exclusiondetails.add(exclusion_details_obj)

            activity_informations.save()

        except Exception as error:
            raise ValidationError(f"Error creating ActivityInformations: {error}")

        return activity_informations

    def update(self, instance, validated_data):
        inclusion_details_data = validated_data.pop('inclusiondetails', [])

        if inclusion_details_data:
            # Update or create inclusion details
            new_inclusion_details_ids = set()
            for inclusion_data in inclusion_details_data:
                inclusion_id = inclusion_data.get('id')
                inclusion_instance = inclusion_data.get('inclusion')

                if inclusion_id:
                    print(1)
                    try:
                        inclusion_obj = ActivityInclusionInformation.objects.get(pk=inclusion_id)
                        ActivityInclusionInformationSerializer().update(instance=inclusion_obj, validated_data=inclusion_data)
                    except ObjectDoesNotExist:
                        raise ValidationError(f"InclusionInformation with ID {inclusion_id} does not exist.")
                else:
                    print(2)
                    if inclusion_instance:
                        inclusion_id = inclusion_instance.id
                        inclusion_data['inclusion'] = inclusion_id
                        print(inclusion_data)
                    inclusion_serializer = ActivityInclusionInformationSerializer(data=inclusion_data)
                    inclusion_serializer.is_valid(raise_exception=True)
                    inclusion_instance = inclusion_serializer.save()
                    instance.inclusiondetails.add(inclusion_instance)
                    new_inclusion_details_ids.add(inclusion_instance.id)

            # Remove old inclusion details that are not present in the request
            old_inclusion_details_ids = instance.inclusiondetails.values_list('id', flat=True)
            inclusion_details_to_delete = set(old_inclusion_details_ids) - set([item.get('id') for item in inclusion_details_data])

            # Exclude newly created inclusion details from deletion
            inclusion_details_to_delete -= new_inclusion_details_ids

            if inclusion_details_to_delete:
                instance.inclusiondetails.filter(id__in=inclusion_details_to_delete).delete()

        instance.save()
        return instance

class ActivityPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityPricing
        exclude = ['status', 'created_on', 'updated_on',]

    # def validate_group_rate(self, value):
    #     if value < 0:
    #         raise ValidationError("Group rate cannot be negative.")
    #     return value

    # def validate_group_commission(self, value):
    #     if value < 0:
    #         raise ValidationError("Group commission cannot be negative.")
    #     return value

    # def validate_adult_rate(self, value):
    #     if value < 0:
    #         raise ValidationError("Adult rate cannot be negative.")
    #     return value

    # def validate_adult_commission(self, value):
    #     if value < 0:
    #         raise ValidationError("Adult commission cannot be negative.")
    #     return value

    # def validate_child_rate(self, value):
    #     if value < 0:
    #         raise ValidationError("Child rate cannot be negative.")
    #     return value

    # def validate_child_commission(self, value):
    #     if value < 0:
    #         raise ValidationError("Child commission cannot be negative.")
    #     return value

    # def validate_infant_rate(self, value):
    #     if value < 0:
    #         raise ValidationError("Infant rate cannot be negative.")
    #     return value

    # def validate_infant_commission(self, value):
    #     if value < 0:
    #         raise ValidationError("Infant commission cannot be negative.")
    #     return value
        
    # def validate(self, data):
    #     # Ensure that group_commission <= group_rate
    #     group_rate = data.get('group_rate')
    #     group_commission = data.get('group_commission')
    #     if group_rate is not None and group_commission is not None and group_commission > group_rate:
    #         raise ValidationError("Group commission cannot be greater than group rate.")

    #     # Ensure that adult_commission <= adult_rate
    #     adult_rate = data.get('adult_rate')
    #     adult_commission = data.get('adult_commission')
    #     if adult_rate is not None and adult_commission is not None and adult_commission > adult_rate:
    #         raise ValidationError("Adult commission cannot be greater than adult rate.")

    #     # Ensure that child_commission <= child_rate
    #     child_rate = data.get('child_rate')
    #     child_commission = data.get('child_commission')
    #     if child_rate is not None and child_commission is not None and child_commission > child_rate:
    #         raise ValidationError("Child commission cannot be greater than child rate.")

    #     # Ensure that infant_commission <= infant_rate
    #     infant_rate = data.get('infant_rate')
    #     infant_commission = data.get('infant_commission')
    #     if infant_rate is not None and infant_commission is not None and infant_commission > infant_rate:
    #         raise ValidationError("Infant commission cannot be greater than infant rate.")

    #     return data


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
                cancellation_category_data = ActivityCancellationCategory.objects.create(**data)
                cancellation_policy.category.add(cancellation_category_data)

        except Exception as error:
            raise serializers.ValidationError(f"Error creating Cancellation Policy: {error}")

        return cancellation_policy

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', [])
        # Update the main CancellationPolicy instance
        instance.activity = validated_data.get('activity', instance.activity)
        instance.save()
        # Clear existing categories
        instance.category.clear()
        # Add new categories
        for data in category_data:
            category_instance = ActivityCancellationCategory.objects.filter(**data)
            if category_instance.exists():
                category_instance = category_instance.first()
            else:
                category_instance, _ = ActivityCancellationCategory.objects.get_or_create(**data)
            instance.category.add(category_instance)
        return instance


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

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', [])
        # Update the main CancellationPolicy instance
        instance.activity = validated_data.get('activity', instance.activity)
        instance.save()
        # Clear existing categories
        instance.category.clear()
        # Add new categories
        for data in category_data:
            category_instance = ActivityFaqCategory.objects.filter(**data)
            if category_instance.exists():
                category_instance = category_instance.first()
            else:
                category_instance, _ = ActivityFaqCategory.objects.get_or_create(**data)
            instance.category.add(category_instance)
        return instance


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

class ActivityImageListSerializer(serializers.Serializer):
    image = serializers.ListField(child=serializers.ImageField())


class HomePageActivitySerializer(serializers.ModelSerializer):
    agent = BookingAgentSerializer(required=False)
    locations = LocationGetSerializer(many=True, required=False)
    activity_image= ActivityImageSerializer(many=True, required=False)
    # pricing_activity = PricingSerializer(many=True,required=False)
    min_price = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    average_review_rating = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ["id","activity_uid","title","tour_class",
                  "locations","agent","activity_image","min_price", "category",
                  "total_reviews","average_review_rating","duration","duration_day",
                  "duration_night","duration_hour", "deal_type"]
        
    def get_min_price(self, obj):
        pricing_activity = obj.pricing_activity.all()
        if pricing_activity.exists():
            min_adults_rate = min(pricing.adults_rate for pricing in pricing_activity)
            return min_adults_rate
        return None
    
    def get_total_reviews(self, obj):
        return obj.activity_review.filter(is_active=True, is_deleted=False).count()
    
    def get_average_review_rating(self, obj):
        user_reviews = obj.activity_review.all()
        if user_reviews.exists():
            average_rating = user_reviews.aggregate(Avg('rating'))['rating__avg']
            return average_rating
        return None