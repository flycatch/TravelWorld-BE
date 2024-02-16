# v1/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.general.viewsets import CityViewSet, StateViewSet, CountryViewSet
from api.v1.agent.viewsets import AgentViewSet, RegisterViewSet, LoginViewSet
from api.v1.package.viewsets import (PackageViewSet, ItineraryViewSet, ItineraryDayViewSet,
                                     PackageInformationsViewSet, PricingViewSet, PackageCategoryViewSet,
                                     PackageCancellationPolicyViewSet, PackageFAQQuestionViewSet,
                                     PackageFAQAnswerViewSet, PackageImageViewSet, PackageDeleteDraft,
                                     PackageTourCategoryViewSet, InclusionsViewSet, ExclusionsViewSet)

from api.v1.bookings.viewsets import *


router = DefaultRouter()

# General
router.register(r'cities', CityViewSet, basename='city')
router.register(r'states', StateViewSet, basename='state')
router.register(r'countries', CountryViewSet, basename='country')

# Agent
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'agent/register', RegisterViewSet, basename='register')
router.register(r'agent/login', LoginViewSet, basename='login')

# Package
router.register(r'package/create', PackageViewSet, basename='package')
router.register(r'packages/upload', PackageImageViewSet, basename='package-image-upload')
router.register(r'packages/delete-draft', PackageDeleteDraft, basename='delete_draft_package'),
# router.register(r'packages/tourtype/', PackageTourTypeViewSet, basename='tour_type'),
router.register(r'packages/category', PackageCategoryViewSet, basename='category'),

# Itinerary
router.register(r'package/itinerary', ItineraryViewSet, basename='itinerary')
router.register(r'package/itineraryday', ItineraryDayViewSet, basename='itinerary-day')

#inclusions and exclusions
router.register(r'package/inclusions', InclusionsViewSet, basename='inclusions')
router.register(r'package/exclusions', ExclusionsViewSet, basename='exclusions')

# Informations
router.register(r'package/informations', PackageInformationsViewSet, basename='informations')

# pricing
router.register(r'package/pricing', PricingViewSet, basename='pricing')
router.register(r'package/tourcategory', PackageTourCategoryViewSet, basename='tourcategory')

router.register(r'package/cancellation', PackageCancellationPolicyViewSet,
                basename='packagecancellation')

router.register(r'package/faqquestion', PackageFAQQuestionViewSet, basename='faqquestions')
router.register(r'package/faqanswer', PackageFAQAnswerViewSet, basename='faqanswers')


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/pay/', start_payment, name="payment"),
    path('v1/<int:user_id>/list-bookings/', CustomerBookingListView.as_view(), name='customer-list-bookings'),
    path('v1/<int:user_id>/customer-booking-details/<str:object_id>/', CustomerBookingDetailsView.as_view(), name='customer-booking-details'),

    path('v1/<int:agent_id>/agent-list-bookings/', AgentBookingListView.as_view(), name='agent-list-bookings'),
    path('v1/<int:agent_id>/agent-booking-details/<str:object_id>/', AgentBookingDetailsView.as_view(), name='agent-booking-details'),

    path('v1/<int:agent_id>/agent-list-transactions/', AgentTransactionListView.as_view(), name='agent-list-transaction'),
    path('v1/<int:agent_id>/agent-transactions-details/<str:object_id>/', AgentTransactionDetailsView.as_view(), name='agent-transactions-details'),



    path('v1/welcome/', WelcomeView.as_view(), name='index'),

]