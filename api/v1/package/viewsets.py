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
from api.v1.activity.serializers import ActivitySerializer
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
from rest_framework.views import exception_handler
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import PackageImageListSerializer


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

        if instance.stage == 'rejected':
            serializer.save(stage="pending") 
        elif not instance.is_submitted:
            serializer.save(is_submitted=True)  # Set is_submitted to True for final submission
        else:
            # Package already submitted, return message
            return Response({'id': instance.id, 
                             'message': 'This package has already been submitted.', 'status': 'Failed',
                             'statusCode':status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'id': instance.id, 
                         'message': 'Successfully submitted package', 'status': 'success', 
                         'statusCode':status.HTTP_200_OK}, status=status.HTTP_200_OK)

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

    def handle_exception(self, exc):
        # Call the default exception handler first to get the standard error response
        response = super().handle_exception(exc)
        
        # Check if the exception is a validation error
        if isinstance(exc, ValidationError):
            # Extract error messages
            error_messages = []
            for field, errors in exc.detail.items():
                for error in errors:
                    error_messages.append(f"{field}: {error}")

        return Response({'message': error_messages, 'status': 'Failed',
                         'statusCode':status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)




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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Itinerary saved',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ItinerarySerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'message': 'Itinerary updated',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


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
        package = self.request.GET.get("package", None)

        queryset = PackageInformations.objects.all()

        if package:
            queryset = queryset.filter(package=package)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'PackageInformations saved',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PackageInformationsSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'status': 'success',
            'message': 'PackageInformations updated',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


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


class PricingNewView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    serializer_class = PricingSerializer
    

    def post(self, request, *args, **kwargs):
        try:

            with transaction.atomic():
                serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid():
                    serializer.save()
                
                    return Response({"message":"Pricing created successfully",
                                "status": "success",
                                "statusCode": status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
                
                else:
                    return Response({ "message": f"Something went wrong : {serializer.errors}",
                                    "status": "error",
                                    "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def get(self, request, *args, **kwargs):
        try:
            package = self.request.GET.get('package',None)
            activity = self.request.GET.get('activity',None)

            if package:
                queryset = Pricing.objects.filter(package=package)
            else:
                queryset = Pricing.objects.filter(activity=activity)

            serializer = self.serializer_class(queryset, many=True)
            return Response({"results":serializer.data,
                            "message":"Listed successfully",
                            "status": "success",
                            "statusCode": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    
        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def put(self, request, *args, **kwargs):
        try:

            with transaction.atomic():

                instance_id = kwargs.get('pk')
                if instance_id is not None:
                    instance = get_object_or_404(Pricing, id=instance_id)
                    serializer = self.serializer_class(instance, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)

                    if serializer.is_valid:
                        return Response({"message":"Pricing updated successfully",
                                "status": "success",
                                "statusCode": status.HTTP_200_OK}, status=status.HTTP_200_OK)

                    else:
                        error_messages = ", ".join([", ".join(errors) for field, errors in serializer.errors.items()])
                        return Response({ 'status': 'error', 'message': error_messages,
                                        'statusCode': status.HTTP_400_BAD_REQUEST },
                                        status=status.HTTP_400_BAD_REQUEST)
                  

        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, *args, **kwargs):
        try:
            instance_id = kwargs.get('pk')
            instance = Pricing.objects.get(pk=instance_id)
            instance.delete()
            
            return Response({
                "message": "Pricing deleted successfully",
                "status": "success",
                "statusCode": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)

        except Pricing.DoesNotExist:
            return Response({
                "message": "Pricing does not exist",
                "status": "error",
                "statusCode": status.HTTP_404_NOT_FOUND
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as error_message:
            response_data = {
                "message": f"Something went wrong: {error_message}",
                "status": "error",
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

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
        package = self.request.GET.get("package", None)
        queryset = CancellationPolicy.objects.all()
        if package:
            queryset = queryset.filter(package=package)
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



class PackageFaqQuestionAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = PackageFaqQuestionAnswerSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]



    def get_queryset(self, **kwargs):
        package = self.request.GET.get("package", None)
        queryset = PackageFaqQuestionAnswer.objects.all()
        if package:
            queryset = queryset.filter(package=package)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Package FAQ saved',
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
            'message': 'Package FAQ updated',
            'id': serializer.data['id'],
            'statusCode': status.HTTP_200_OK
        }, status=status.HTTP_200_OK)


class PackageImageUploadView(generics.CreateAPIView, generics.ListAPIView, 
                             generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = PackageImage.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = PackageImageListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        package_id = request.query_params.get('package')
        if package_id:
            images = PackageImage.objects.filter(package_id=package_id)
            serializer = PackageImageSerializer(images, many=True)
            return Response(serializer.data)
        else:
            return Response({'status': 'failed', 'message': 'Please provide a package id',
                             'error':serializer.errors,
                             'statusCode': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            images = serializer.validated_data['image']
            package_id = request.data.get('package')  # Make sure to pass package_id with the request
            package = Package.objects.get(pk=package_id)

            for image in images:
                PackageImage.objects.create(package=package, image=image)
            
            return Response({'status': 'success', 'message': 'Images uploaded successfully',
                             'statusCode': status.HTTP_200_OK}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'failed', 'message': 'Images upload failed',
                             'error':serializer.errors,
                             'statusCode': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'status': 'success', 'message': 'Image deleted successfully'},
                        status=status.HTTP_204_NO_CONTENT)


class PopularPackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.filter(is_submitted=True)
    serializer_class = PackageGetSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    filterset_class = PackageFilter
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    # def get_queryset(self, **kwargs):
    #     print(Package.objects.filter(is_submitted=True))
    #     return Package.objects.filter(is_submitted=True)


class PopularActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Activity.objects.filter(is_submitted=True)
    serializer_class = ActivitySerializer
    pagination_class = CustomPagination
    # filterset_class = ActivityFilter
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]


class PopularProductsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = None  # Will be determined dynamically
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        activities = Activity.objects.filter(is_submitted=True)
        packages = Package.objects.filter(is_submitted=True)
        return list(activities) + list(packages)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Determine serializer based on object type
        if queryset:
            if isinstance(queryset[0], Activity):
                self.serializer_class = ActivitySerializer
            elif isinstance(queryset[0], Package):
                self.serializer_class = PackageSerializer
        else:
            return Response([])
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
