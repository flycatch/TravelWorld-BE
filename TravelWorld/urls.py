from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import api

schema_view = get_schema_view(
    openapi.Info(
        title="TravelWorld API",
        default_version='v1',
        description="API documentation for TravelWorld",
        # terms_of_service="https://www.travelworld.com/terms/",
        # contact=openapi.Contact(email="contact@travelworld.com"),
        # license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/dashboard/', api.admin.dashboard_page, name='dashboard_page'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    #Swagger and ReDoc documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
