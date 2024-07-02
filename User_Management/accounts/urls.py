# v1/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.v1.agent.viewsets import (AgentViewSet, RegisterViewSet, LoginViewSet,ForgotPassword,
                                   CustomPasswordResetConfirmView,AgentBankDetailsAPIView,WelcomeView)

from accounts.v1.user.viewsets import (UserViewSet, UserRegisterViewSet, UserLoginViewset, UserForgotPassword,
                                        UserCustomPasswordResetConfirmView)
from accounts.v1.social_logins.viewsets import *



router = DefaultRouter()



# Agent
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'agent/register', RegisterViewSet, basename='register')
router.register(r'agent/login', LoginViewSet, basename='login')
router.register(r'agent/bank-details', AgentBankDetailsAPIView, basename='agent-bank-details')

#User
router.register(r'users', UserViewSet, basename='user')
router.register(r'user/register', UserRegisterViewSet, basename='user-register')
router.register(r'user/login', UserLoginViewset, basename='user-login')









# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('v1/', include(router.urls)),
    

    #Forgot password
    path('v1/forgot-password-link/', ForgotPassword.as_view(), name='forgot-password'),
    path('v1/reset-password/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('v1/user/forgot-password-link/', UserForgotPassword.as_view(), name='user-forgot-password'),
    path('v1/user/reset-password/', UserCustomPasswordResetConfirmView.as_view(), name='user-password_reset_confirm'),


    path('v1/welcome/', WelcomeView.as_view(), name='index'),

    # google logins
    path("v1/google/callback", GoogleLoginApi.as_view(), name="callback-raw"),
    path("v1/google/redirect/", GoogleLoginRedirectApi.as_view(), name="redirect-raw"),

    path("v1/facebook/redirect/", FacebookLoginRedirectApi.as_view(), name="facebook-redirect-raw"),
    path('v1/facebook/callback', fb_login,name='fb_login'),



]