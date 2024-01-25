# v1/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.agent.viewsets import AgentViewSet, RegisterViewSet, LoginViewSet


router = DefaultRouter()
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'agent/register', RegisterViewSet, basename='register')
router.register(r'agent/login', LoginViewSet, basename='login')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('v1/', include(router.urls)),
]