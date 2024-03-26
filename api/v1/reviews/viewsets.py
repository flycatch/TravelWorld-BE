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
from api.filters.review_filters import ReviewFilter
from django.utils import timezone
from django.db.models import Q,Count,Avg



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
        # request.data['user'] = kwargs['user_id']
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                if serializer.is_valid():
                    serializer.save(is_active=True)
                    message = 'Created successfully'
                    return Response({"message": message,
                                  "status": "success",
                                "statusCode": status.HTTP_201_CREATED
                                  }, status=status.HTTP_201_CREATED)
                

                else:
                    return Response({ "results": serializer.errors,
                                    "message": "Something went wrong",
                                    "status": "error",
                                    "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

                
            
        
        
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
    

    def update(self, request, *args, **kwargs):
       
        instance = get_object_or_404(
            self.get_queryset(), object_id=kwargs.get('object_id'))
        serializer = self.serializer_class(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        message = 'updated successfully'
        return Response({"message" : message,
                          "status": "success",
                        "statusCode": status.HTTP_200_OK},status=status.HTTP_200_OK)

        


class UserReviewListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserReviewDetailSerializer
    pagination_class = CustomPagination
    filterset_class = ReviewFilter
    
    def get_queryset(self):
        queryset =  UserReview.objects.filter(user=self.kwargs['user_id'],is_deleted=0, is_active=1).order_by("-id")
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
        
        
        




class UserReviewActionView(viewsets.GenericViewSet):
    """
    This API view handles CRUD operations related to UserReview Reply Views.

    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserReviewSerializer
    # queryset = UserReview.objects.filter(is_deleted=0, is_active=1)


    def update(self, request, *args, **kwargs):

        """
        Updates a specific user reply view.
        """

        try:
            
           
            instance = UserReview.objects.get(object_id=kwargs.get('object_id'))
            serializer = self.serializer_class(
                instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            if serializer.is_valid():
                serializer.save(agent_reply_date=timezone.now())

            else:
                return Response({ "results": serializer.errors,
                                "message": "Something went wrong",
                                "status": "error",
                                "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            message = 'updated successfully'
            return Response({"message" : message,
                            "status": "success",
                            "statusCode": status.HTTP_200_OK},status=status.HTTP_200_OK)
        
        except Exception as error_message:
                response_data = {"message": f"Something went wrong: {error_message}",
                                "status": "error",
                                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE request to mark a user_review as deleted.

        Args:
            **kwargs: Additional keyword arguments, including 'object_id'.

        Returns:
            Response: The HTTP response indicating successful deletion.

        """
        try:
            UserReview.objects.filter(object_id=kwargs.get('object_id')).update(
                agent_comment=None,
                agent_reply_date=None,
                agent=None
            )
            
            message = 'Deleted successfully'
            return Response({"message" : message,
                          "status": "success",
                        "statusCode": status.HTTP_200_OK},status=status.HTTP_200_OK)
        
        except Exception as error_message:
                response_data = {"message": f"Something went wrong: {error_message}",
                                "status": "error",
                                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AgentUserReviewListView(ListAPIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    serializer_class = UserReviewDetailSerializer
    pagination_class = CustomPagination
    filterset_class = ReviewFilter

    
    def get_queryset(self):
        queryset =  UserReview.objects.filter(is_deleted=0, is_active=1).order_by("-id")
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
        
        
            
class UserRatingsView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    

    def get(self, request, *args, **kwargs):
        try:
            package = self.request.GET.get('package',None)
            activity = self.request.GET.get('activity',None)
            queryset =  UserReview.objects.filter(is_deleted=0, is_active=1).order_by("-id")

            if package:
                queryset = queryset.filter(package=package)
            else:
                queryset = queryset.filter(activity=activity)

            
            # Get total review count for each rating
            total_reviews = queryset.aggregate(
                total=Count('id'),
                rating_5=Count('id', filter=Q(rating=5)),
                rating_4=Count('id', filter=Q(rating=4)),
                rating_3=Count('id', filter=Q(rating=3)),
                rating_2=Count('id', filter=Q(rating=2)),
                rating_1=Count('id', filter=Q(rating=1)),
                rating_avg = Avg('rating')
            )

            results = {
                "total_reviews": total_reviews['total'],
                "rating_5_count": total_reviews['rating_5'],
                "rating_4_count": total_reviews['rating_4'],
                "rating_3_count": total_reviews['rating_3'],
                "rating_2_count": total_reviews['rating_2'],
                "rating_1_count": total_reviews['rating_1'],
                "rating_avg": total_reviews['rating_avg']
            }

            return Response({
                "results": results,
                "message": "Listed successfully",
                "status": "success",
                "statusCode": status.HTTP_200_OK
            }, status=status.HTTP_200_OK)
    
        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)