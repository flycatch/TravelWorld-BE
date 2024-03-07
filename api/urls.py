# v1/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.general.viewsets import CityViewSet, StateViewSet, CountryViewSet
from api.v1.agent.viewsets import AgentViewSet, RegisterViewSet, LoginViewSet,ForgotPassword,CustomPasswordResetConfirmView
from api.v1.package.viewsets import (PackageViewSet, ItineraryViewSet, ItineraryDayViewSet,
                                     PackageInformationsViewSet, PricingViewSet, PackageCategoryViewSet,
                                     PackageCancellationPolicyViewSet, PackageFaqQuestionAnswerViewSet,
                                     PackageImageViewSet, PackageDeleteDraft, PackageTourCategoryViewSet,
                                     InclusionsViewSet, ExclusionsViewSet)
from api.v1.activity.viewsets import (ActivityViewSet, ActivityItineraryViewSet, ActivityItineraryDayViewSet,
                                     ActivityInformationsViewSet, ActivityPricingViewSet, ActivityCategoryViewSet,
                                     ActivityCancellationPolicyViewSet, ActivityFaqQuestionAnswerViewSet,
                                     ActivityImageViewSet, ActivityDeleteDraft, ActivityTourCategoryViewSet,
                                     ActivityInclusionsViewSet, ActivityExclusionsViewSet)
from api.v1.user.viewsets import (UserViewSet, UserRegisterViewSet, UserLoginViewset, UserForgotPassword, UserCustomPasswordResetConfirmView)
from api.v1.bookings.viewsets import *
from api.v1.reviews.viewsets import *
from api.v1.social_logins.viewsets import *


router = DefaultRouter()

# General
router.register(r'cities', CityViewSet, basename='city')
router.register(r'states', StateViewSet, basename='state')
router.register(r'countries', CountryViewSet, basename='country')

# Agent
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'agent/register', RegisterViewSet, basename='register')
router.register(r'agent/login', LoginViewSet, basename='login')

#User
router.register(r'users', UserViewSet, basename='user')
router.register(r'user/register', UserRegisterViewSet, basename='user-register')
router.register(r'user/login', UserLoginViewset, basename='user-login')

"""
Package urls
"""
router.register(r'package/create', PackageViewSet, basename='package') #package crud operations
router.register(r'packages/upload', PackageImageViewSet, basename='package-image-upload')
router.register(r'packages/delete-draft', PackageDeleteDraft, basename='delete_draft_package'),
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
router.register(r'package/faq', PackageFaqQuestionAnswerViewSet, basename='package_faq')

"""
Activity urls
"""
router.register(r'activity/create', ActivityViewSet, basename='activity') #activity crud operations
router.register(r'activity/upload', ActivityImageViewSet, basename='activity_image_upload')
router.register(r'activity/delete-draft', ActivityDeleteDraft, basename='delete_draft_activity'),
router.register(r'activity/category', ActivityCategoryViewSet, basename='activity_category'),

# Itinerary
router.register(r'activity/itinerary', ActivityItineraryViewSet, basename='activity_itinerary')
router.register(r'activity/itineraryday', ActivityItineraryDayViewSet, basename='activity_itinerary-day')

#inclusions and exclusions
router.register(r'activity/inclusions', ActivityInclusionsViewSet, basename='activity_inclusions')
router.register(r'activity/exclusions', ActivityExclusionsViewSet, basename='activity_exclusions')

# Informations
router.register(r'activity/informations', ActivityInformationsViewSet, basename='activity_informations')

# pricing
router.register(r'activity/pricing', ActivityPricingViewSet, basename='activity_pricing')
router.register(r'activity/tourcategory', ActivityTourCategoryViewSet, basename='activity_tourcategory')

router.register(r'activity/cancellation', ActivityCancellationPolicyViewSet,
                basename='activitycancellation')

router.register(r'activity/faq', ActivityFaqQuestionAnswerViewSet, basename='activity_faq')


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('v1/', include(router.urls)),
    
    # User booking
    path('v1/pay/', start_payment, name="payment"),
    path('v1/<int:user_id>/customer-list-bookings/', CustomerBookingListView.as_view(), name='customer-list-bookings'),
    path('v1/<int:user_id>/customer-booking-details/<str:object_id>/', CustomerBookingDetailsView.as_view(), name='customer-booking-details'),


    # Agent View booking
    path('v1/<int:agent_id>/agent-list-bookings/', AgentBookingListView.as_view(), name='agent-list-bookings'),
    path('v1/<int:agent_id>/agent-booking-details/<str:object_id>/', AgentBookingDetailsView.as_view(), name='agent-booking-details'),

    # Agent View transaction
    path('v1/<int:agent_id>/agent-list-transactions/', AgentTransactionListView.as_view(), name='agent-list-transaction'),
    path('v1/<int:agent_id>/agent-transactions-details/<str:object_id>/', AgentTransactionDetailsView.as_view(), name='agent-transactions-details'),

    #Forgot password
    path('v1/forgot-password-link/', ForgotPassword.as_view(), name='forgot-password'),
    path('v1/reset-password/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('v1/user/forgot-password-link/', UserForgotPassword.as_view(), name='user-forgot-password'),
    path('v1/user/reset-password/', UserCustomPasswordResetConfirmView.as_view(), name='user-password_reset_confirm'),

    #User Review
    path('v1/<int:user_id>/user-review/', UserReviewView.as_view
         ({
             'post': 'create'
         }), name='user-review'),

    path('v1/<int:user_id>/user-review-list/', UserReviewListView.as_view(), name='user-review-list'),

    path('v1/<int:user_id>/user-review/<str:object_id>/', UserReviewView.as_view
         ({
             'delete': 'destroy'
         }), name='user-review-detail'),

    path('v1/agent/user-review-reply/<str:object_id>/', AgentUserReviewReplyView.as_view
         ({
             'patch': 'update'
         }), name='user-review-reply'),
    
    path('v1/agent/user-review-reply-list/', AgentUserReviewReplyListView.as_view(), name='user-review-reply-list'),

    path('v1/advance-amount-percentage-list/', AdvanceAmountPercentageSettingListView.as_view(), name='advance-amount-percentage-list'),

    path('v1/welcome/', WelcomeView.as_view(), name='index'),

    # google logins
    path("v1/google/callback", GoogleLoginApi.as_view(), name="callback-raw"),
    path("v1/google/redirect/", GoogleLoginRedirectApi.as_view(), name="redirect-raw"),

    path("v1/facebook/redirect/", FacebookLoginRedirectApi.as_view(), name="facebook-redirect-raw"),
    path('v1/facebook/callback', fb_login,name='fb_login'),

]