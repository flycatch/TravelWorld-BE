# views.py
from api.filters.package_activity_filters import *
from api.models import (CancellationPolicy, Exclusions, Inclusions, Itinerary,
                        ItineraryDay, Package, PackageCategory,
                        PackageFaqQuestionAnswer, PackageImage,
                        PackageInformations, Pricing, TourCategory)
from api.utils.paginator import CustomPagination
from api.v1.package.serializers import (ExclusionsSerializer,
                                        InclusionsSerializer,
                                        ItineraryDaySerializer,
                                        ItinerarySerializer,
                                        PackageCancellationPolicySerializer,
                                        PackageCategorySerializer,
                                        PackageFaqQuestionAnswerSerializer,
                                        PackageImageSerializer,
                                        PackageInformationsSerializer,
                                        PackageSerializer,
                                        PackageTourCategorySerializer,
                                        PricingSerializer)
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q


class PackageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations related to packages.
    """

    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['agent__username','package_uid','title','tour_class'] 
    filterset_class = PackageFilter

    def get_queryset(self, **kwargs):
        """
        Queryset to list package data based on agent if passed agent id as param.
        also sort data option added.
        Get the queryset of packages filtered by status, stage, and submission.

        Returns:
            queryset: A filtered queryset containing active and approved packages that are submitted.
        """

        queryset = Package.objects.all()
        #sort
        sort_by = self.request.GET.get("sort_by", None)
        sort_order = self.request.GET.get("sort_order", "asc")
        agent = self.request.GET.get("agent")

        if agent:
            queryset = Package.objects.filter(agent=agent)

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
            returns package id as response.
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Check if the instance has already been submitted
        if instance.is_submitted:
            raise ValidationError({'detail': 'This package has already been submitted.'})
        
        serializer.save(is_submitted=True)  # Set is_submitted to True for final submission
        return Response({'id': instance.id, 'status': 'submitted'})

    def create(self, request, *args, **kwargs):
        """
        Create a new Package.

        Args:
            request: The request object containing the data for the new package.
        Returns:
            Response: A response with created package id.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Package saved',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)


class PackageImageViewSet(viewsets.ModelViewSet):
    queryset = PackageImage.objects.all()
    serializer_class = PackageImageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        images_data = request.FILES.getlist('image')
        package_id = request.data.get('package')
        try:
            package = Package.objects.get(pk=package_id)
        except Package.DoesNotExist:
            return Response({'message': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)

        for image in images_data:
            try:
                PackageImage.objects.create(package=package, image=image)
            except Exception as error_message:
                return Response({'message': str(error_message)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'Image upload successful'}, status=status.HTTP_201_CREATED)


class PackageDeleteDraft(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def destroy(self, request, *args, **kwargs):
        try:
            package = Package.objects.get(pk=kwargs['pk'])
            # Check if the package belongs to the authenticated user
            if package.agent.id == request.user.id:
                if not package.is_submitted:
                    package.delete()
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


class ItineraryViewSet(viewsets.ModelViewSet):
    serializer_class = ItinerarySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self, **kwargs):
        package = self.request.GET.get("package",None)

        queryset = Itinerary.objects.all()


        if package:
            queryset = queryset.filter(package=package)
        
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


class InclusionsViewSet(viewsets.ModelViewSet):
    serializer_class = InclusionsSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self, **kwargs):
        package = self.request.GET.get("package",None)

        queryset = Inclusions.objects.all()

        if package:
            queryset = queryset.filter(Q(package__isnull=True) | Q(package=package))
        else:
            queryset = queryset.filter(package__isnull=True)
        return queryset
    
    
class ExclusionsViewSet(viewsets.ModelViewSet):
    serializer_class = ExclusionsSerializer

    def get_queryset(self, **kwargs):
        package = self.request.GET.get("package",None)

        queryset = Exclusions.objects.all()

        if package:
            queryset = queryset.filter(Q(package__isnull=True) | Q(package=package))
        else:
            queryset = queryset.filter(package__isnull=True)
        return queryset


class ItineraryDayViewSet(viewsets.ModelViewSet):
    queryset = ItineraryDay.objects.all()
    serializer_class = ItineraryDaySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


#Informations
class PackageInformationsViewSet(viewsets.ModelViewSet):
    serializer_class = PackageInformationsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self, **kwargs):
        package = self.request.GET.get("package",None)

        queryset = PackageInformations.objects.all()

        if package:
            queryset = queryset.filter(package=package)
        
        return queryset


class PricingViewSet(viewsets.ModelViewSet):
    serializer_class = PricingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self, **kwargs):
        package = self.request.GET.get("package",None)

        queryset = Pricing.objects.all()

        if package:
            queryset = queryset.filter(package=package)
        
        return queryset



class PackageCategoryViewSet(viewsets.ModelViewSet):
    queryset = PackageCategory.objects.all()
    serializer_class = PackageCategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class PackageTourCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = PackageTourCategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self, **kwargs):
        package = self.request.GET.get("package",None)

        queryset = TourCategory.objects.all()

        if package:
            queryset = queryset.filter(package=package)
        
        return queryset


class PackageCancellationPolicyViewSet(viewsets.ModelViewSet):
    serializer_class = PackageCancellationPolicySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self, **kwargs):
        package = self.request.GET.get("package",None)

        queryset = CancellationPolicy.objects.all()

        if package:
            queryset = queryset.filter(package=package)
        
        return queryset


class PackageFaqQuestionAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = PackageFaqQuestionAnswerSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


    def get_queryset(self, **kwargs):
        package = self.request.GET.get("package",None)

        queryset = PackageFaqQuestionAnswer.objects.all()

        if package:
            queryset = queryset.filter(package=package)
        
        return queryset

