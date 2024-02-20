import razorpay
from api.filters.booking_filters import *
from api.models import *
from api.tasks import *
from api.utils.paginator import CustomPagination
from api.v1.reviews.serializers import *
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
from django.db import transaction



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
        Handle POST request to create a new freight charges.

        Args:
            request (Request): The HTTP POST request object.
            **kwargs: Additional keyword arguments, including 'created_by'.

        Returns:
            Response: The HTTP response containing the serialized freight charges data.

        """
        request.data['created_by'] = kwargs['user_id']
        try:
            with transaction.atomic():
              
               

                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                freight_charge_obj = serializer.save()

                

                
                message = 'created successfully'
                return Response({"message": message, 'data': serializer.data}, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as error:
            response_data = error.detail
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)