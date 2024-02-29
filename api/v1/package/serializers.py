# serializers.py
import decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import (Package, Itinerary, ItineraryDay, PackageInformations, Pricing,
                        TourCategory,CancellationPolicy, PackageFaqCategory, PackageFaqQuestionAnswer,
                        PackageImage, PackageCategory, Inclusions, Exclusions,
                        InclusionInformation, ExclusionInformation, PackageCancellationCategory)
from api.v1.agent.serializers import BookingAgentSerializer
from api.v1.general.serializers import *



class PackageSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    agent_name = serializers.CharField(source='agent.agent_uid', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = Package
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
            raise ValidationError("Error creating package: {}".format(str(error)))


class PackageImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageImage
        exclude = ['status', 'created_on', 'updated_on',]


# class PackageTourTypeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TourType
#         exclude = ['status']


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


class InclusionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inclusions
        fields = ['id', 'name','package']


class ExclusionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exclusions
        fields = ['id', 'name','package']


class InclusionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InclusionInformation
        fields = ['inclusion', 'details',]


class ExclusionInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExclusionInformation
        fields = ['exclusion', 'details',]


class PackageInformationsSerializer(serializers.ModelSerializer):
    inclusiondetails = InclusionInformationSerializer(many=True, required=False)
    exclusiondetails = ExclusionInformationSerializer(many=True, required=False)
    class Meta:
        model = PackageInformations
        exclude = ['status', 'created_on', 'updated_on',]

    def create(self, validated_data):
        inclusion_details_data = validated_data.pop('inclusiondetails', None)
        exclusion_details_data = validated_data.pop('exclusiondetails', None)

        try:
            package_informations = PackageInformations.objects.create(**validated_data)

            if inclusion_details_data:
                for inclusion_data in inclusion_details_data:
                    inclusion_details_obj = InclusionInformation.objects.create(**inclusion_data)
                    package_informations.inclusiondetails.add(inclusion_details_obj)

            if exclusion_details_data:
                for exclusion_data in exclusion_details_data:
                    exclusion_details_obj = ExclusionInformation.objects.create(**exclusion_data)
                    package_informations.exclusiondetails.add(exclusion_details_obj)

            package_informations.save()

        except Exception as error:
            raise ValidationError(f"Error creating PackageInformations: {error}")

        return package_informations

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['packageinformation_id'] = instance.id
    #     return data


class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pricing
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
                print(data)
                cancellation_category_data = PackageCancellationCategory.objects.create(**data)
                cancellation_policy.category.add(cancellation_category_data)
        except Exception as error:
            raise serializers.ValidationError(f"Error creating Cancellation Policy: {error}")

        return cancellation_policy

    # def validate(self, data):
    #     from_day = data.get('from_day')
    #     to_day = data.get('to_day')
    #     amount_percent = data.get('amount_percent')

    #     # Add your custom validation logic here
    #     if from_day is not None and to_day is not None:
    #         if from_day >= to_day:
    #             raise ValidationError("The 'from_day' must be less than 'to_day'.")

    #     if amount_percent is not None:
    #         try:
    #             amount_percent = float(amount_percent)
    #             if amount_percent < 0 or amount_percent > 100:
    #                 raise ValidationError("The 'amount percentage' must be between 0 and 100.")
    #         except ValueError:
    #             raise ValidationError("Invalid value for 'amount percentage'. Must be a number.")

    #     return data



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


class BookingPackageSerializer(serializers.ModelSerializer):
    agent = BookingAgentSerializer(required=False)
    city = CitySerializer(required=False)
    state = StateSerializer(required=False)
    country = CountrySerializer(required=False)

    class Meta:
        model = Package
        fields = ["id","package_uid","title","tour_class",
                  "country","state","city","agent"]
        

class PackageMinFieldsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Package
        fields = ['id','package_uid','title']