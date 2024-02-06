# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from api.models import (Package, Itinerary, ItineraryDay, Informations, Guide,
                        InformationActivities, ThingsToCarry, HotelDetails, Pricing,
                        TourCategory, CancellationPolicy, FAQQuestion, FAQAnswer)
from api.v1.package.serializers import (PackageSerializer, ItinerarySerializer, 
                                        ItineraryDaySerializer, InformationsSerializer, 
                                        GuideSerializer, InformationActivitiesSerializer,
                                        ThingsToCarrySerializer, HotelDetailsSerializer,
                                        PricingSerializer, PackageCategorySerializer,
                                        PackageCancellationPolicySerializer,
                                        PackageFAQQuestionSerializer,
                                        PackageFAQAnswerSerializer)


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer


#Itinerary
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


class HotelDetailsViewSet(viewsets.ModelViewSet):
    queryset = HotelDetails.objects.all()
    serializer_class = HotelDetailsSerializer


class GuideViewSet(viewsets.ModelViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer


class InformationActivitiesViewSet(viewsets.ModelViewSet):
    queryset = InformationActivities.objects.all()
    serializer_class = InformationActivitiesSerializer


class ThingsToCarryViewSet(viewsets.ModelViewSet):
    queryset = ThingsToCarry.objects.all()
    serializer_class = ThingsToCarrySerializer


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