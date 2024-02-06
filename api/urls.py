# v1/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.agent.viewsets import AgentViewSet, RegisterViewSet, LoginViewSet
from api.v1.package.viewsets import (PackageViewSet, ItineraryViewSet, ItineraryDayViewSet,
                                     InformationsViewSet, GuideViewSet, InformationActivitiesViewSet,
                                     ThingsToCarryViewSet, HotelDetailsViewSet)


router = DefaultRouter()
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'agent/register', RegisterViewSet, basename='register')
router.register(r'agent/login', LoginViewSet, basename='login')

#Package
router.register(r'package', PackageViewSet, basename='package')
#Itinerary
router.register(r'itinerary', ItineraryViewSet, basename='itinerary')
router.register(r'itineraryday', ItineraryDayViewSet, basename='itinerary-day')
#Informations
router.register(r'informations', InformationsViewSet, basename='informations')
router.register(r'hoteldetails', HotelDetailsViewSet, basename='hotel-details')
router.register(r'guide', GuideViewSet, basename='guide')
router.register(r'informationactivity', InformationActivitiesViewSet, basename='information-activity')
router.register(r'thingstocarry', ThingsToCarryViewSet, basename='things-to-carry')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('v1/', include(router.urls)),
]
