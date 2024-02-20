import razorpay
from api.filters.booking_filters import *
from api.models import *
from api.tasks import *
from api.utils.paginator import CustomPagination
from api.v1.reviews.serializers import *
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from TravelWorld.settings import *
from django.shortcuts import get_object_or_404


class UserReviewView(viewsets.GenericViewSet):
    """
    This API view handles CRUD operations related to UserReviewViews.

    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserReviewSerializer
    queryset = UserReview.objects.filter(is_deleted=0, is_active=1)

   
    def create(self, request, *args, **kwargs):
        """
        Handle POST request to create a new user review.

        Args:
            request (Request): The HTTP POST request object.
            **kwargs: Additional keyword arguments, including 'created_by'.

        Returns:
            Response: The HTTP response containing the serialized user review data.

        """
        request.data['created_by'] = kwargs['user_id']
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response({ "results": serializer.errors,
                                    "message": "Something went wrong",
                                    "status": "error",
                                    "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

                message = 'Created successfully'
                return Response({"message": message,
                                  "status": "success",
                                "statusCode": status.HTTP_201_CREATED
                                  }, status=status.HTTP_201_CREATED)
            
        
        
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE request to mark a sales lead as deleted.

        Args:
            **kwargs: Additional keyword arguments, including 'object_id'.

        Returns:
            Response: The HTTP response indicating successful deletion.

        """
        queryset = self.get_queryset()
        object_id = self.kwargs.get('object_id')
        
        instance = get_object_or_404(queryset, object_id=object_id)

        queryset.filter(object_id=object_id).update(
            is_deleted=True,
            is_active=False
        )
        message = 'Deleted successfully'
        return Response({"message" : message,
                          "status": "success",
                        "statusCode": status.HTTP_200_OK},status=status.HTTP_200_OK)
        


class UserReviewListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserReviewDetailSerializer
    pagination_class = CustomPagination

    
    def get_queryset(self):
        try:
            queryset =  UserReview.objects.filter(created_by=self.kwargs['user_id'],is_deleted=0, is_active=1).order_by("-id")
            return queryset
        
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)