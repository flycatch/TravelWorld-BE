# serializers.py
import decimal

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from api.models import (Package, Itinerary, PackageInformations, Pricing, SuitableFor,
                        TourCategory,CancellationPolicy, PackageFaqCategory, PackageFaqQuestionAnswer,
                        PackageImage, PackageCategory, Inclusions, Exclusions, Location,
                        InclusionInformation, ExclusionInformation, PackageCancellationCategory,
                        FavoriteProducts, ItineraryDay, InclusionExclusion, Informations, StayDetails)
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
        exclude = ['status', 'is_popular', "deal_type"]

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
        activities_data = validated_data.pop('activities', [])
        suitable_for_data = validated_data.pop('suitable_for', [])
        
        package = Package.objects.create(**validated_data)

        for location_data in locations_data:
            try:
                destination_ids = location_data.pop('destinations', [])
                locations_obj = Location.objects.create(**location_data)
                locations_obj.destinations.set(destination_ids)
                package.locations.add(locations_obj)

            except Exception as error:
                raise serializers.ValidationError(error)

        package.activities.set(activities_data)
        package.suitable_for.set(suitable_for_data)

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


class PackageImageSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and creating PackageImage instances.

    Meta:
        model (PackageImage): The model that this serializer is for.
        exclude (list): Fields to exclude from the serialization.
    """
    class Meta:
        model = PackageImage
        exclude = ['status', 'created_on', 'updated_on',]


class InclusionSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing Inclusions model objects.

    **Fields:**

    * id (IntegerField): Primary key of the Inclusion object.
    * name (CharField): Name of the inclusion.
    * package (PrimaryKeyRelatedField): Reference to the Package 
        the inclusion belongs to.
    """
    class Meta:
        model = Inclusions
        fields = ['id', 'name']


class ExclusionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exclusions
        fields = ['id', 'name', 'package']


class ItineraryDaySerializer(serializers.ModelSerializer):
    """
    This serializer is used for creating, updating, and retrieving ItineraryDay data.

    **Fields:**
    * id (IntegerField, optional): Primary key of the ItineraryDay object (read-only during creation).
    * day (CharField): Day of the itinerary (e.g., "Day 1", "Day 2").
    * place (CharField, optional): Place to be visited on this day.
    * description (CKEditor5Field, optional): Description of the activities or events planned for this day.

    **Meta:**
    * model: ItineraryDay
    * fields: '__all__'  # Include all fields from the model
    """
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ItineraryDay
        fields = ['id', 'day', 'place', 'description']


class ItinerarySerializer(serializers.ModelSerializer):
    """
    This serializer is used for creating, updating, and retrieving Itinerary data,
    including nested ItineraryDay objects.

    **Fields:**
    * package (Foreignkey): Package model object.
    * overview (CKEditor5Field): Overview of the itinerary (uses CKEditor 5 config named 'extends').
    * itinerary_day (ItineraryDaySerializer, many=True, required=False): Nested ItineraryDay
        serializers for itinerary days.

    **Meta:**
    * model: Itinerary
    * exclude: ['status', 'created_on', 'updated_on']  # Exclude these fields during serialization

    **Methods:**
    * get_exclusions_details(self, obj): Returns a list of serialized Exclusions data.
    * create(self, validated_data): Creates a new Itinerary object and related entities.
    * update(self, instance, validated_data): Updates an existing Itinerary object and related entities.

    **Raises:**
    * ValidationError: If errors occur during data processing.
    """
    itinerary_day = ItineraryDaySerializer(many=True, required=False)

    class Meta:
        model = Itinerary
        exclude = ['status', 'created_on', 'updated_on']

    def create(self, validated_data):
        """
        Creates a new Itinerary instance along with related inclusions, exclusions,
        and itinerary day entities.

        Args:
            validated_data (dict): Validated data for creating the Itinerary instance.

        Returns:
            Itinerary: The newly created Itinerary instance.

        Raises:
            ValidationError: If an error occurs during the creation process.
        """
        itinerary_day_data = validated_data.pop('itinerary_day', [])

        try:
            #create itinerary instance
            itinerary = Itinerary.objects.create(**validated_data)

            #create itinerary_day object and map into itinerary
            for day_data in itinerary_day_data:
                itinerary_day_obj = ItineraryDay.objects.create(**day_data)
                itinerary.itinerary_day.add(itinerary_day_obj)

        except Exception as error:
            raise ValidationError(f"Error creating Itinerary: {error}")

        return itinerary

    def update(self, instance, validated_data):
        """
        Updates an existing Itinerary instance along with related inclusions, exclusions,
        and itinerary day entities.

        Args:
            instance (Itinerary): The existing Itinerary instance to be updated.
            validated_data (dict): Validated data for updating the Itinerary instance.

        Returns:
            Itinerary: The updated Itinerary instance.

        Raises:
            ValidationError: If an error occurs during the update process.
        """
        itinerary_day_data = validated_data.pop('itinerary_day', None)

        # Update the main Itinerary instance
        instance.overview = validated_data.get('overview', instance.overview)

        #update itinerary_day object if data has id esle create.
        for itinerary_day in itinerary_day_data:
            itinerary_day_id = itinerary_day.get('id')
            if itinerary_day_id:
                try:
                    itinerary_day_obj = ItineraryDay.objects.get(pk=itinerary_day_id)
                    ItineraryDaySerializer().update(instance=itinerary_day_obj, validated_data=itinerary_day)
                except ItineraryDay.DoesNotExist:
                    raise serializers.ValidationError(f"Itinerary Day with id {itinerary_day_id} does not exist.")
            else:
                itinerary_day_obj = ItineraryDay.objects.create(**itinerary_day)
                instance.itinerary_day.add(itinerary_day_obj)

        instance.save()
        return instance


class InclusionExclusionSerializer(serializers.ModelSerializer):
    """
    Serializer for creating, updating, and retrieving InclusionExclusion instances,
    with nested inclusion data.

    Attributes:
        inclusions_data (InclusionSerializer): Serialized data for the inclusions related to the 
        InclusionExclusion instance.

    Meta:
        model (InclusionExclusion): The model that this serializer is for.
        fields (list): Fields to include in the serialization.
    """
    inclusions_data = InclusionSerializer(many=True, read_only=True,source='inclusions')

    class Meta:
        model = InclusionExclusion
        fields = ['id', 'package', 'inclusions_data', 'inclusion_details',
                  'exclusion_details', 'inclusions']

    def create(self, validated_data):
        """
        Creates a new InclusionExclusion instance and sets the related inclusions.

        Args:
            validated_data (dict): The validated data for creating the InclusionExclusion instance.

        Returns:
            InclusionExclusion: The created InclusionExclusion instance.

        Raises:
            ValidationError: If an error occurs while creating the instance.
        """
        inclusions_data = validated_data.pop('inclusions', [])

        try:
            #create inclusions and exclusions instance
            inclusion_exclusion = InclusionExclusion.objects.create(**validated_data)
            inclusion_exclusion.inclusions.set(inclusions_data)

        except Exception as error:
            raise ValidationError(f"Error Creating Inclusions and Exclusions Data: {error}")

        return inclusion_exclusion

    def update(self, instance, validated_data):
        """
        Updates an existing InclusionExclusion instance and its related inclusions.

        Args:
            instance (InclusionExclusion): The existing instance to update.
            validated_data (dict): The validated data for updating the InclusionExclusion instance.

        Returns:
            InclusionExclusion: The updated InclusionExclusion instance.

        Raises:
            ValidationError: If an error occurs while updating the instance.
        """
        inclusions_data = validated_data.pop('inclusions', None)

        # Update the main inclusions and exclusions instance
        instance.inclusion_details = validated_data.get('inclusion_details', instance.inclusion_details)
        instance.exclusion_details = validated_data.get('exclusion_details', instance.exclusion_details)

        # Update inclusions if data provided
        if inclusions_data is not None:
            instance.inclusions.set(inclusions_data)

        instance.save()
        return instance


class StayDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing StayDetails model objects.
    This serializer is used for serializing StayDetails objects during API requests.

    **Fields:**

    * `id` (IntegerField, required=False): Primary key of the StayDetails object 
        (can be omitted during creation).
    * `place` (CharField): Name of the place where the stay will happen.
    * `hotel_name` (CharField): Name of the hotel or accommodation for the stay.

    **Meta:**

    * `model`: StayDetails
    * `fields`: ['id', 'place', 'hotel_name']

    **Note:**

    * The `id` field is not required during object creation, as it will be generated automatically.
    """
    id = serializers.IntegerField(required=False)

    class Meta:
        model = StayDetails
        fields = ['id', 'place', 'hotel_name']


class InformationSerializer(serializers.ModelSerializer):
    """
    Serializer for serializing Informations model objects.
    This serializer is used for creating and updating Informations objects related to Packages,
    including nested StayDetails data.

    **Fields:**

    * `id` (IntegerField, read-only): Primary key of the Information object.
    * `package` (ForeignKey to Package model): Reference to the Package this information belongs to.
    * `things_to_carry` (CKEditor5Field): Textual information about things to carry for the trip.
    * `stay_details` (StayDetailsSerializer, many=True): Nested serializer for managing StayDetails
        objects associated with the information.

    **Methods:**

    * `create(self, validated_data)`: Creates a new Information object and associated StayDetails
        objects from the provided data.
    * `update(self, instance, validated_data)`: Updates an existing Information object and associated
        StayDetails objects based on the provided data.
    """
    stay_details = StayDetailsSerializer(many=True)

    class Meta:
        model = Informations
        fields = ['id', 'package', 'things_to_carry', 'stay_details']

    def create(self, validated_data):
        """
        Create a new Informations instance along with nested StayDetails instances.

        Args:
            validated_data (dict): The validated data containing information for creating
            Informations and nested StayDetails instances.

        Returns:
            Informations: The newly created Informations instance.

        Raises:
            ValidationError: If an error occurs during the creation process.
        """
        stay_details_data = validated_data.pop('stay_details', [])

        try:
            # Create informations instance
            informations = Informations.objects.create(**validated_data)

            # Create stay_data objects and map into informations
            for stay_data in stay_details_data:
                stay_details_obj = StayDetails.objects.create(**stay_data)
                informations.stay_details.add(stay_details_obj)

        except Exception as error:
            raise ValidationError(f"Error Creating Informations Data: {error}")

        return informations

    def update(self, instance, validated_data):
        """
        Update an existing Informations instance along with nested StayDetails instances.

        Args:
            instance (Informations): The existing Informations instance to update.
            validated_data (dict): The validated data containing updated information for Informations 
            and nested StayDetails instances.

        Returns:
            Informations: The updated Informations instance.

        Raises:
            ValidationError: If a StayDetails instance with the given ID does not exist.
        """
        stay_details_data = validated_data.pop('stay_details', [])

        # Update the main informations instance
        instance.things_to_carry = validated_data.get('things_to_carry', instance.things_to_carry)

        #update stay_data object if data has id esle create.
        for stay_data in stay_details_data:
            stay_data_id = stay_data.get('id')
            if stay_data_id:
                try:
                    stay_data_obj = StayDetails.objects.get(pk=stay_data_id)
                    StayDetailsSerializer().update(instance=stay_data_obj, validated_data=stay_data)
                except StayDetails.DoesNotExist:
                    raise serializers.ValidationError(f"Stay Details with id {stay_data_id} does not exist.")
            else:
                stay_details_obj = StayDetails.objects.create(**stay_data)
                instance.stay_details.add(stay_details_obj)

        instance.save()
        return instance


class InclusionInformationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(source='inclusion.name', read_only=True, required=False)
    # inclusion = serializers.PrimaryKeyRelatedField(queryset=Inclusions.objects.all(), required=False)

    class Meta:
        model = InclusionInformation
        fields = ['id', 'inclusion', 'name', 'details',]


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

            package_informations.save()

        except Exception as error:
            raise ValidationError(f"Error creating PackageInformations: {error}")

        return package_informations

    def update(self, instance, validated_data):
        inclusion_details_data = validated_data.pop('inclusiondetails', [])

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


#Renamed as activities
class PackageCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageCategory
        fields = ['id', 'name']


class SuitableForSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuitableFor
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
                category_instance, _ = PackageCancellationCategory.objects.get_or_create(**data)
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
                category_instance, _ = PackageFaqCategory.objects.get_or_create(**data)
            instance.category.add(category_instance)
        return instance


class BookingPackageSerializer(serializers.ModelSerializer):
    agent = BookingAgentSerializer(required=False)
    locations = LocationGetSerializer(many=True,required=False)
    package_image= PackageImageSerializer(many=True, required=False)


    class Meta:
        model = Package
        fields = ["id","package_uid","title","tour_class",
                  "agent","package_image","locations"]
        
from decimal import Decimal

class HomePagePackageSerializer(serializers.ModelSerializer):
    agent = BookingAgentSerializer(required=False)
    locations = LocationGetSerializer(many=True,required=False)
    package_image= PackageImageSerializer(many=True, required=False)
    # pricing_package = PricingSerializer(many=True,required=False)
    min_price = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    average_review_rating = serializers.SerializerMethodField()
    activities = HomePageCategorySerializer(many=True,required=False)
    suitable_for = HomePageSuitableForSerializer(many=True,required=False)

    class Meta:
        model = Package
        fields = ["id","package_uid","title","tour_class", "agent","package_image","min_price",
                  "price", "activities", "suitable_for", "total_reviews","average_review_rating",
                  "duration","duration_day", "duration_night","duration_hour","locations", 
                  "min_members", "max_members", "deal_type","is_recommended", "is_popular"]
        
    def get_min_price(self, obj):
        pricing_packages = obj.pricing_package.all()
        if pricing_packages.exists():
            min_adults_rate = min(pricing.adults_rate for pricing in pricing_packages)
            return min_adults_rate
        return None
        
    def get_price(self, obj):
        pricing_packages = obj.pricing_package.all()
        if pricing_packages.exists():
            min_adults_rate = min(pricing.adults_rate for pricing in pricing_packages)
            discount = pricing_packages.first().discount if pricing_packages.first().discount else 0
            return self.calculate_discounted_price(min_adults_rate, discount)
        return None

    def calculate_discounted_price(self, actual_price, discount):
        if discount is None or discount == 0:
            return {"actual_price": actual_price, "discounted_price": None}
        
        discount_decimal = Decimal(str(discount))  # Convert discount to Decimal
        discounted_price = actual_price * (1 - discount_decimal / 100)
        return {"actual_price": actual_price, "discounted_price": discounted_price}
    
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


class FavoriteProductSerializer(serializers.ModelSerializer):
    package = HomePagePackageSerializer(required=False)

    class Meta:
        model = FavoriteProducts
        fields = ['id', 'user', 'package']
