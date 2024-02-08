# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from api.models import (Package, Itinerary, ItineraryDay, Informations, Pricing,
                        TourCategory, CancellationPolicy, FAQQuestion, FAQAnswer,
                        PackageImage)
from api.v1.package.serializers import (PackageSerializer, ItinerarySerializer, 
                                        ItineraryDaySerializer, InformationsSerializer, 
                                        PricingSerializer, PackageCategorySerializer,
                                        PackageFAQQuestionSerializer,PackageImageSerializer,
                                        PackageCancellationPolicySerializer,
                                        PackageFAQAnswerSerializer)


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

    @action(detail=True, methods=['patch'], url_path='submit')
    def submit_final(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_submitted=True)  # Set is_submitted to True for final submission
        return Response({'id': instance.id, 'status': 'submitted'})


class PackageImageViewSet(viewsets.ModelViewSet):
    queryset = PackageImage.objects.all()
    serializer_class = PackageImageSerializer

    def create(self, request, *args, **kwargs):
        images_data = request.FILES.getlist('image')  # Get list of uploaded images
        package_id = request.data.get('package')
        package = Package.objects.get(pk=package_id)
        
        for image in images_data:
            PackageImage.objects.create(package=package, image=image)
        return Response({'message': 'Image upload successful'}, status=status.HTTP_201_CREATED)


class ItineraryViewSet(viewsets.ModelViewSet):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer


class ItineraryDayViewSet(viewsets.ModelViewSet):
    queryset = ItineraryDay.objects.all()
    serializer_class = ItineraryDaySerializer


#Informations
class InformationsViewSet(viewsets.ModelViewSet):
    queryset = Informations.objects.all()
    serializer_class = InformationsSerializer


class PricingViewSet(viewsets.ModelViewSet):
    queryset = Pricing.objects.all()
    serializer_class = PricingSerializer


class PackageCategoryViewSet(viewsets.ModelViewSet):
    queryset = TourCategory.objects.all()
    serializer_class = PackageCategorySerializer


class PackageCancellationPolicyViewSet(viewsets.ModelViewSet):
    queryset = CancellationPolicy.objects.all()
    serializer_class = PackageCancellationPolicySerializer


class PackageFAQQuestionViewSet(viewsets.ModelViewSet):
    queryset = FAQQuestion.objects.all()
    serializer_class = PackageFAQQuestionSerializer

class PackageFAQAnswerViewSet(viewsets.ModelViewSet):
    queryset = FAQAnswer.objects.all()
    serializer_class = PackageFAQAnswerSerializer