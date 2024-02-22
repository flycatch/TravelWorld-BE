# views.py
from api.filters.package_activity_filters import *
from api.models import (Activity, ActivityCancellationPolicy, ActivityCategory,
                        ActivityExclusions, ActivityFaqQuestionAnswer,
                        ActivityImage, ActivityInclusions,
                        ActivityInformations, ActivityItinerary,
                        ActivityItineraryDay, ActivityPricing,
                        ActivityTourCategory)
from api.utils.paginator import CustomPagination
from api.v1.activity.serializers import (ActivityCancellationPolicySerializer,
                                         ActivityCategorySerializer,
                                         ActivityExclusionsSerializer,
                                         ActivityFaqQuestionAnswerSerializer,
                                         ActivityImageSerializer,
                                         ActivityInclusionsSerializer,
                                         ActivityInformationsSerializer,
                                         ActivityItineraryDaySerializer,
                                         ActivityItinerarySerializer,
                                         ActivityPricingSerializer,
                                         ActivitySerializer,
                                         ActivityTourCategorySerializer)
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class ActivityViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations related to activities.
    """
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['agent__username','activity_uid','title','tour_class'] 
    filterset_class = ActivityFilter


    def get_queryset(self, **kwargs):
        """
        Queryset to list activity data based on agent if passed agent id as param.
        also sort data option added.
        Get the queryset of packages filtered by status, stage, and submission.

        Returns:
            queryset: A filtered queryset containing active and approved packages that are submitted.
        """

        queryset = Activity.objects.all()
        # sort
        sort_by = self.request.GET.get("sort_by", None)
        sort_order = self.request.GET.get("sort_order", "asc")
        agent = self.request.GET.get("agent")

        if agent:
            queryset = queryset.filter(agent=agent)

        if sort_by:
            sort_field = sort_by if sort_order == "asc" else f"-{sort_by}"
            queryset = queryset.order_by(sort_field)
        
        return queryset

    @action(detail=True, methods=['patch'], url_path='submit')
    @transaction.atomic
    def submit_final(self, request, pk=None):
        """
        function to make activity final submit true, while calling patch method.
        
        Returns:
            returns activity id as response.
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Check if the instance has already been submitted
        if instance.is_submitted:
            raise ValidationError({'detail': 'This activity has already been submitted.'})
        
        serializer.save(is_submitted=True)  # Set is_submitted to True for final submission
        return Response({'id': instance.id, 'status': 'submitted'})

    def create(self, request, *args, **kwargs):
        """
        Create a new activity.

        Args:
            request: The request object containing the data for the new activity.
        Returns:
            Response: A response with created activity id.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Activity saved',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)


class ActivityImageViewSet(viewsets.ModelViewSet):
    queryset = ActivityImage.objects.all()
    serializer_class = ActivityImageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        images_data = request.FILES.getlist('image')
        activity_id = request.data.get('activity')
        try:
            activity = Activity.objects.get(pk=activity_id)
        except Activity.DoesNotExist:
            return Response({'message': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)

        for image in images_data:
            try:
                ActivityImage.objects.create(activity=activity, image=image)
            except Exception as error_message:
                return Response({'message': str(error_message)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'Image upload successful'}, status=status.HTTP_201_CREATED)


class ActivityDeleteDraft(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def delete(self, request, *args, **kwargs):
        try:
            activity = self.get_object()
            # Check if the activity belongs to the authenticated user
            if activity.user == request.user:
                if not activity.is_submitted:
                    activity.delete()
                    return Response({'message': 'Activity deleted successfully'},
                                    status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({'message': 'Cannot delete a submitted activity'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'You do not have permission to delete this activity'},
                                status=status.HTTP_403_FORBIDDEN)
        except Activity.DoesNotExist:
            return Response({'message': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)


# class ActivityTourTypeViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = TourType.objects.all()
#     serializer_class = ActivityTourTypeSerializer


class ActivityItineraryViewSet(viewsets.ModelViewSet):
    queryset = ActivityItinerary.objects.all()
    serializer_class = ActivityItinerarySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Itinerary saved',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)


class ActivityInclusionsViewSet(viewsets.ModelViewSet):
    queryset = ActivityInclusions.objects.all()
    serializer_class = ActivityInclusionsSerializer


class ActivityExclusionsViewSet(viewsets.ModelViewSet):
    queryset = ActivityExclusions.objects.all()
    serializer_class = ActivityExclusionsSerializer


class ActivityItineraryDayViewSet(viewsets.ModelViewSet):
    queryset = ActivityItineraryDay.objects.all()
    serializer_class = ActivityItineraryDaySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


#Informations
class ActivityInformationsViewSet(viewsets.ModelViewSet):
    queryset = ActivityInformations.objects.all()
    serializer_class = ActivityInformationsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ActivityPricingViewSet(viewsets.ModelViewSet):
    queryset = ActivityPricing.objects.all()
    serializer_class = ActivityPricingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ActivityCategoryViewSet(viewsets.ModelViewSet):
    queryset = ActivityCategory.objects.all()
    serializer_class = ActivityCategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ActivityTourCategoryViewSet(viewsets.ModelViewSet):
    queryset = ActivityTourCategory.objects.all()
    serializer_class = ActivityTourCategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ActivityCancellationPolicyViewSet(viewsets.ModelViewSet):
    queryset = ActivityCancellationPolicy.objects.all()
    serializer_class = ActivityCancellationPolicySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ActivityFaqQuestionAnswerViewSet(viewsets.ModelViewSet):
    queryset = ActivityFaqQuestionAnswer.objects.all()
    serializer_class = ActivityFaqQuestionAnswerSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
