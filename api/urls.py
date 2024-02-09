# v1/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.agent.viewsets import AgentViewSet, RegisterViewSet, LoginViewSet
from api.v1.package.viewsets import (PackageViewSet, ItineraryViewSet, ItineraryDayViewSet,
                                     InformationsViewSet, PricingViewSet, PackageCategoryViewSet,
                                     PackageCancellationPolicyViewSet, PackageFAQQuestionViewSet,
                                     PackageFAQAnswerViewSet, PackageImageViewSet, PackageDeleteDraft)


router = DefaultRouter()
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'agent/register', RegisterViewSet, basename='register')
router.register(r'agent/login', LoginViewSet, basename='login')

# Package
router.register(r'package/create', PackageViewSet, basename='package')
router.register(r'packages/upload', PackageImageViewSet, basename='package-image-upload')
router.register(r'packages/delete-draft/', PackageDeleteDraft, basename='delete_draft_package'),

# Itinerary
router.register(r'package/itinerary', ItineraryViewSet, basename='itinerary')
router.register(r'package/itineraryday', ItineraryDayViewSet, basename='itinerary-day')
# Informations
router.register(r'package/informations', InformationsViewSet, basename='informations')
# router.register(r'package/hoteldetails', HotelDetailsViewSet, basename='hotel-details')
# router.register(r'package/guide', GuideViewSet, basename='guide')
# router.register(r'package/informationactivity', InformationActivitiesViewSet,
#                 basename='information-activity')
# router.register(r'package/thingstocarry', ThingsToCarryViewSet, basename='things-to-carry')

# pricing
router.register(r'package/pricing', PricingViewSet, basename='pricing')
router.register(r'package/category', PackageCategoryViewSet, basename='packagecategory')

router.register(r'package/cancellation', PackageCancellationPolicyViewSet,
                basename='packagecancellation')

router.register(r'package/faqquestion', PackageFAQQuestionViewSet, basename='faqquestions')
router.register(r'package/faqanswer', PackageFAQAnswerViewSet, basename='faqanswers')


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('v1/', include(router.urls)),
]