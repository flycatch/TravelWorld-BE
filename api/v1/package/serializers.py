# serializers.py
import decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from api.models import (Package, Itinerary, ItineraryDay, PackageInformations, Pricing,
                        TourCategory,CancellationPolicy, PackageFaqCategory, PackageFaqQuestionAnswer,
                        PackageImage, PackageCategory, Inclusions, Exclusions, Location,
                        InclusionInformation, ExclusionInformation, PackageCancellationCategory)
from api.v1.agent.serializers import BookingAgentSerializer
from api.v1.general.serializers import *
from api.v1.general.serializers import LocationSerializer
from django.db.models import Avg


class PackageSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.agent_uid', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    locations = LocationSerializer(many=True, required=False)

    class Meta:
        model = Package
        exclude = ['status', 'is_submitted', 'is_popular']

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
        package = Package.objects.create(**validated_data)

        for location_data in locations_data:
            try:
                destination_ids = location_data.pop('destinations', [])
                locations_obj = Location.objects.create(**location_data)
                locations_obj.destinations.set(destination_ids)
                package.locations.add(locations_obj)

            except Exception as error:
                raise serializers.ValidationError(error)

        return package


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
    

class PackageGetSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.agent_uid', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    locations = LocationGetSerializer(many=True, required=False)

    class Meta:
        model = Package
        exclude = ['status', 'is_submitted']


class PackageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImage
        exclude = ['status', 'created_on', 'updated_on',]


class ItineraryDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItineraryDay
        exclude = ['status', 'created_on', 'updated_on']


class ItinerarySerializer(serializers.ModelSerializer):
    itinerary_day = ItineraryDaySerializer(many=True)

    class Meta:
        model = Itinerary
        exclude = ['status', 'created_on', 'updated_on']

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

    def update(self, instance, validated_data):
        itinerary_day_data = validated_data.pop('itinerary_day', None)
        inclusions_data = validated_data.pop('inclusions', None)
        exclusions_data = validated_data.pop('exclusions', None)

        # Update the main Itinerary instance
        instance.overview = validated_data.get('overview', instance.overview)

        # Update or create itinerary day objects using id if data provided
        if itinerary_day_data is not None:
            for itinerary_day in instance.itinerary_day.all():
                itinerary_day_id = itinerary_day.id
                for day_data in itinerary_day_data:
                    day_serializer = ItineraryDaySerializer(instance=itinerary_day, data=day_data, partial=True)
                    day_serializer.is_valid(raise_exception=True)
                    day_instance = day_serializer.save()
                    instance.itinerary_day.add(day_instance)

        # Update inclusions if data provided
        if inclusions_data is not None:
            instance.inclusions.set(inclusions_data)

        # Update exclusions if data provided
        if exclusions_data is not None:
            instance.exclusions.set(exclusions_data)

        instance.save()
        return instance


class InclusionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inclusions
        fields = ['id', 'name']


class ExclusionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exclusions
        fields = ['id', 'name']


class InclusionInformationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    # inclusion = serializers.PrimaryKeyRelatedField(queryset=Inclusions.objects.all(), required=False)

    class Meta:
        model = InclusionInformation
        fields = ['id', 'inclusion', 'details',]


class ExclusionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExclusionInformation
        fields = ['id', 'exclusion', 'details',]


class PackageInformationsSerializer(serializers.ModelSerializer):
    inclusiondetails = InclusionInformationSerializer(many=True, required=False)
    exclusiondetails = ExclusionInformationSerializer(many=True, required=False)
    class Meta:
        model = PackageInformations
        exclude = ['status', 'created_on', 'updated_on',]

    def create(self, validated_data):
        inclusion_details_data = validated_data.pop('inclusiondetails', None)
        # exclusion_details_data = validated_data.pop('exclusiondetails', None)

        try:
            package_informations = PackageInformations.objects.create(**validated_data)

            if inclusion_details_data:
                for inclusion_data in inclusion_details_data:
                    inclusion_details_obj = InclusionInformation.objects.create(**inclusion_data)
                    package_informations.inclusiondetails.add(inclusion_details_obj)

            # if exclusion_details_data:
            #     for exclusion_data in exclusion_details_data:
            #         exclusion_details_obj = ExclusionInformation.objects.create(**exclusion_data)
            #         package_informations.exclusiondetails.add(exclusion_details_obj)

            package_informations.save()

        except Exception as error:
            raise ValidationError(f"Error creating PackageInformations: {error}")

        return package_informations

    def update(self, instance, validated_data):
        inclusion_details_data = validated_data.pop('inclusiondetails', [])

        instance.important_message = validated_data.get('important_message', instance.important_message)

        if inclusion_details_data:
            # Update or create inclusion details
            new_inclusion_details_ids = set()
            for inclusion_data in inclusion_details_data:
                inclusion_id = inclusion_data.get('id')
                inclusion_instance = inclusion_data.get('inclusion')

                if inclusion_id:
                    try:
                        inclusion_obj = InclusionInformation.objects.get(pk=inclusion_id)
                        InclusionInformationSerializer().update(instance=inclusion_obj, validated_data=inclusion_data)
                    except ObjectDoesNotExist:
                        raise ValidationError(f"InclusionInformation with ID {inclusion_id} does not exist.")
                else:
                    if inclusion_instance:
                        inclusion_id = inclusion_instance.id
                        inclusion_data['inclusion'] = inclusion_id
                    inclusion_serializer = InclusionInformationSerializer(data=inclusion_data)
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




class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        exclude = ['status', 'created_on', 'updated_on',]


class PackageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageCategory
        fields = ['id', 'name']



class PackageTourCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TourCategory
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


class CancellationPolicyCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageCancellationCategory
        fields = ['from_day', 'to_day', 'amount_percent',]


class PackageCancellationPolicySerializer(serializers.ModelSerializer):
    category = CancellationPolicyCategorySerializer(many=True, required=False)

    class Meta:
        model = CancellationPolicy
        exclude = ['status', 'created_on', 'updated_on',]

    def create(self, validated_data):
        category_data = validated_data.pop('category', [])

        try:
            cancellation_policy = CancellationPolicy.objects.create(**validated_data)

            for data in category_data:
                cancellation_category_data = PackageCancellationCategory.objects.create(**data)
                cancellation_policy.category.add(cancellation_category_data)
        except Exception as error:
            raise serializers.ValidationError(f"Error creating Cancellation Policy: {error}")

        return cancellation_policy

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', [])
        # Update the main CancellationPolicy instance
        instance.package = validated_data.get('package', instance.package)
        instance.save()
        # Clear existing categories
        instance.category.clear()
        # Add new categories
        for data in category_data:
            category_instance = PackageCancellationCategory.objects.filter(**data)
            if category_instance.exists():
                category_instance = category_instance.first()
            else:
                category_instance = PackageCancellationCategory.objects.get_or_create(**data)
            instance.category.add(category_instance)
        return instance



class PackageFaqCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageFaqCategory
        fields = ['question', 'answer',]


class PackageFaqQuestionAnswerSerializer(serializers.ModelSerializer):
    category = PackageFaqCategorySerializer(many=True, required=False)
    class Meta:
        model = PackageFaqQuestionAnswer
        exclude = ['status', 'created_on', 'updated_on',]

    def create(self, validated_data):
        category_data = validated_data.pop('category', [])

        try:
            package_faq_data = PackageFaqQuestionAnswer.objects.create(**validated_data)

            for data in category_data:
                print(data)
                faq_category_data = PackageFaqCategory.objects.create(**data)
                package_faq_data.category.add(faq_category_data)
        except Exception as error:
            raise serializers.ValidationError(f"Error creating Package FAQ: {error}")

        return package_faq_data

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', [])
        # Update the main CancellationPolicy instance
        instance.package = validated_data.get('package', instance.package)
        instance.save()
        # Clear existing categories
        instance.category.clear()
        # Add new categories
        for data in category_data:
            category_instance = PackageFaqCategory.objects.filter(**data)
            if category_instance.exists():
                category_instance = category_instance.first()
            else:
                category_instance = PackageFaqCategory.objects.get_or_create(**data)
            instance.category.add(category_instance)
        return instance


class BookingPackageSerializer(serializers.ModelSerializer):
    agent = BookingAgentSerializer(required=False)
    city = CitySerializer(required=False)
    state = StateSerializer(required=False)
    country = CountrySerializer(required=False)
    package_image= PackageImageSerializer(many=True, required=False)


    class Meta:
        model = Package
        fields = ["id","package_uid","title","tour_class",
                  "country","state","city","agent","package_image"]
        

class HomePagePackageSerializer(serializers.ModelSerializer):
    agent = BookingAgentSerializer(required=False)
    city = CitySerializer(required=False)
    state = StateSerializer(required=False)
    country = CountrySerializer(required=False)
    package_image= PackageImageSerializer(many=True, required=False)
    # pricing_package = PricingSerializer(many=True,required=False)
    min_price = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    average_review_rating = serializers.SerializerMethodField()




    class Meta:
        model = Package
        fields = ["id","package_uid","title","tour_class",
                  "country","state","city","agent","package_image","min_price","total_reviews","average_review_rating"]
        
    def get_min_price(self, obj):
        pricing_packages = obj.pricing_package.all()
        if pricing_packages.exists():
            min_adults_rate = min(pricing.adults_rate for pricing in pricing_packages)
            return min_adults_rate
        return None
    
    def get_total_reviews(self, obj):
        return obj.package_review.filter(is_active=True, is_deleted=False).count()
    
    def get_average_review_rating(self, obj):
        user_reviews = obj.package_review.all()
        if user_reviews.exists():
            average_rating = user_reviews.aggregate(Avg('rating'))['rating__avg']
            return average_rating
        return None
        

class PackageMinFieldsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Package
        fields = ['id','package_uid','title']



class PackageImageListSerializer(serializers.Serializer):
    image = serializers.ListField(child=serializers.ImageField())