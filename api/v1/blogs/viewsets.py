from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,status
from django.db.models import Count
from django.utils import timezone

from api.models import Country, State, City, CoverPageInput,Attraction, Location,Package,Activity,Booking,Blogs
from api.v1.blogs.serializers import (BlogSerializer)
from api.filters.general_filters import CityFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from api.utils.paginator import CustomPagination
from django.db import transaction
from api.tasks import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated



class BlogListView(ListAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = BlogSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        queryset =  Blogs.objects.filter(is_active=1).order_by("-id")
        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as error_message:
            response_data = {
                "message": f"Something went wrong: {error_message}",
                "status": "error",
                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        