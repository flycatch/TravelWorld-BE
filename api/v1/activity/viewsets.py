# views.py
from api.filters.package_activity_filters import *
from api.models import (Activity, ActivityCancellationPolicy, PackageCategory,
                         ActivityFaqQuestionAnswer, ActivityImage,
                        ActivityInformations, ActivityItinerary, ActivityPricing,
                        ActivityTourCategory, Inclusions, Exclusions)
from api.utils.paginator import CustomPagination
from api.v1.activity.serializers import (ActivityCancellationPolicySerializer,
                                         ActivityCategorySerializer,
                                         ActivityExclusionsSerializer,
                                         ActivityFaqQuestionAnswerSerializer,
                                         ActivityImageSerializer,
                                         ActivityInclusionsSerializer,
                                         ActivityInformationsSerializer,
                                         ActivityItinerarySerializer,
                                         ActivityPricingSerializer,
                                         ActivitySerializer,
                                         ActivityTourCategorySerializer,
                                         ActivityImageListSerializer,
                                         HomePageActivitySerializer)
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q


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
        
        if instance.stage == 'rejected':
            serializer.save(stage="pending") 
        elif not instance.is_submitted:
            serializer.save(is_submitted=True,stage="pending")  # Set is_submitted to True for final submission
        else:
            # activity already submitted, return message
            return Response({'id': instance.id, 
                             'message': 'This activity has already been submitted.', 'status': 'error',
                             'statusCode':status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'id': instance.id, 
                         'message': 'Successfully submitted activity', 'status': 'success', 
                         'statusCode':status.HTTP_200_OK}, status=status.HTTP_200_OK)

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

    def destroy(self, request, *args, **kwargs):
        try:
            activity = Activity.objects.get(pk=kwargs['pk'])
            # Check if the package belongs to the authenticated user
            if activity.agent.id == request.user.id:
                if not activity.is_submitted:
                    activity.delete()
                    return Response({'status':'success', 'message': 'Package deleted successfully',
                                     'statusCode':status.HTTP_200_OK}, status=status.HTTP_200_OK)
                else:
                    return Response({'status':'error', 'message': 'Cannot delete a submitted package',
                                     'statusCode':status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status':'error', 'message': 'You do not have permission to delete this package',
                                 'statusCode':status.HTTP_403_FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
        except Package.DoesNotExist:
            return Response({'status':'error', 'message': 'Package not found',
                             'statusCode':status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)


class ActivityItineraryViewSet(viewsets.ModelViewSet):
    queryset = ActivityItinerary.objects.all()
    serializer_class = ActivityItinerarySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []
        else:
            return super().get_permissions()

    def get_queryset(self, **kwargs):
        activity = self.request.GET.get("activity", None)
        queryset = super().get_queryset()
        if activity:
            queryset = queryset.filter(activity=activity)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Itinerary saved',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'message': 'Itinerary updated',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class ActivityInclusionsViewSet(viewsets.ModelViewSet):
    queryset = Inclusions.objects.all()
    serializer_class = ActivityInclusionsSerializer

    def get_queryset(self, **kwargs):
        
        activity = self.request.GET.get("activity",None)
        queryset = Inclusions.objects.all()

        if activity:
            queryset = queryset.filter(Q(activity__isnull=True) | Q(activity=activity))
        else:
            queryset = queryset.filter(activity__isnull=True)
        return queryset


class ActivityExclusionsViewSet(viewsets.ModelViewSet):
    queryset = Exclusions.objects.all()
    serializer_class = ActivityExclusionsSerializer

    def get_queryset(self, **kwargs):
        activity = self.request.GET.get("activity",None)

        queryset = Exclusions.objects.all()

        if activity:
            queryset = queryset.filter(Q(activity__isnull=True) | Q(activity=activity))
        else:
            queryset = queryset.filter(activity__isnull=True)
        return queryset


#Informations
class ActivityInformationsViewSet(viewsets.ModelViewSet):
    serializer_class = ActivityInformationsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []
        else:
            return super().get_permissions()

    def get_queryset(self, **kwargs):
        activity = self.request.GET.get("activity",None)

        queryset = ActivityInformations.objects.all()

        if activity:
            queryset = queryset.filter(activity=activity)
        
        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'ActivityInformations saved',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ActivityInformationsSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'message': 'ActivityInformations updated',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)

class ActivityPricingViewSet(viewsets.ModelViewSet):
    queryset = ActivityPricing.objects.all()
    serializer_class = ActivityPricingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self, **kwargs):
        activity = self.request.GET.get("activity",None)

        queryset = ActivityPricing.objects.all()

        if activity:
            queryset = queryset.filter(activity=activity)
        
        return queryset


class ActivityCategoryViewSet(viewsets.ModelViewSet):
    queryset = PackageCategory.objects.all()
    serializer_class = ActivityCategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ActivityTourCategoryViewSet(viewsets.ModelViewSet):
    queryset = ActivityTourCategory.objects.all()
    serializer_class = ActivityTourCategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ActivityCancellationPolicyViewSet(viewsets.ModelViewSet):
    serializer_class = ActivityCancellationPolicySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self, **kwargs):
        activity = self.request.GET.get("activity",None)

        queryset = ActivityCancellationPolicy.objects.all()

        if activity:
            queryset = queryset.filter(activity=activity)
        
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Cancellation Policy saved',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_201_CREATED
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'message': 'Cancellation Policy updated',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class ActivityFaqQuestionAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = ActivityFaqQuestionAnswerSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []
        else:
            return super().get_permissions()


    def get_queryset(self, **kwargs):
        activity = self.request.GET.get("activity",None)

        queryset = ActivityFaqQuestionAnswer.objects.all()

        if activity:
            queryset = queryset.filter(activity=activity)
        
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Activity FAQ saved',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_201_CREATED
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'message': 'Activity FAQ updated',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class ActivityImageUploadView(generics.CreateAPIView, generics.ListAPIView, 
                             generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = ActivityImage.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ActivityImageListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        activity_id = request.query_params.get('activity')
        if activity_id:
            images = ActivityImage.objects.filter(activity_id=activity_id)
            serializer = ActivityImageSerializer(images, many=True,  context={'request': request})
            return Response(serializer.data)
        else:
            return Response({'status': 'error',
                             'message': 'Please provide a activity id',
                             'statusCode': status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            images = serializer.validated_data['image']
            activity_id = request.data.get('activity')  # Make sure to pass activity_id with the request

            if activity_id is not None:
                try:
                    activity = Activity.objects.get(pk=activity_id)

                    for image in images:
                        ActivityImage.objects.create(activity=activity, image=image)
                    
                    return Response({'status': 'success', 'message': 'Images uploaded successfully',
                                    'statusCode': status.HTTP_200_OK}, status=status.HTTP_200_OK)
                except Activity.DoesNotExist:
                    return Response({'status': 'error', 'message': 'Activity not found',
                                    'statusCode': status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'status': 'error', 'message': 'Activity ID is required',
                                'statusCode': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'error', 'message': 'Images upload failed',
                             'error':serializer.errors,
                             'statusCode': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'status': 'success', 'message': 'Image deleted successfully'},
                        status=status.HTTP_204_NO_CONTENT)



class ActivityHomePageView(generics.ListAPIView):
    serializer_class = HomePageActivitySerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['user__username','booking_id'] 
    filterset_class = ActivityFilter
    
    
    def get_queryset(self):
        queryset = Activity.objects.filter(is_submitted=True, status='active', stage='approved').order_by("-id")
        return queryset
    
    def apply_additional_filters(self, queryset):
        price_range_min = self.request.query_params.get('price_range_min')
        price_range_max = self.request.query_params.get('price_range_max')
        if price_range_min is not None and price_range_max is not None:
            queryset = queryset.filter(
                Q(pricing_activity__adults_rate__gte=price_range_min) &
                Q(pricing_activity__adults_rate__lte=price_range_max)
            ).distinct()
        return queryset
        
        
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            queryset = self.apply_additional_filters(queryset)

            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as error_message:
            response_data = {
                "message": f"Something went wrong: {error_message}",
                "status": "error",
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

