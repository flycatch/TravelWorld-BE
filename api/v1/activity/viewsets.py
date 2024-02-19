# views.py
from django.db import transaction

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from api.models import (Activity, ActivityItinerary, ActivityItineraryDay, ActivityInformations, 
                        ActivityPricing, ActivityTourCategory, ActivityCancellationPolicy,
                        ActivityFaqQuestionAnswer, ActivityImage, ActivityCategory, ActivityInclusions,
                        ActivityExclusions)
from api.v1.activity.serializers import (ActivitySerializer, ActivityItinerarySerializer, 
                                        ActivityItineraryDaySerializer, ActivityInformationsSerializer, 
                                        ActivityPricingSerializer, ActivityTourCategorySerializer,
                                        ActivityFaqQuestionAnswerSerializer,ActivityImageSerializer, 
                                        ActivityCancellationPolicySerializer, ActivityCategorySerializer,
                                        ActivityInclusionsSerializer, ActivityExclusionsSerializer)


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @action(detail=True, methods=['patch'], url_path='submit')
    @transaction.atomic
    def submit_final(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Check if the instance has already been submitted
        if instance.is_submitted:
            raise ValidationError({'detail': 'This activity has already been submitted.'})
        
        serializer.save(is_submitted=True)  # Set is_submitted to True for final submission
        return Response({'id': instance.id, 'status': 'submitted'})

    def create(self, request, *args, **kwargs):
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


class ItineraryViewSet(viewsets.ModelViewSet):
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


class InclusionsViewSet(viewsets.ModelViewSet):
    queryset = ActivityInclusions.objects.all()
    serializer_class = ActivityInclusionsSerializer


class ExclusionsViewSet(viewsets.ModelViewSet):
    queryset = ActivityExclusions.objects.all()
    serializer_class = ActivityExclusionsSerializer


class ItineraryDayViewSet(viewsets.ModelViewSet):
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


class PricingViewSet(viewsets.ModelViewSet):
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
