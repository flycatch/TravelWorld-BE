from datetime import datetime

import razorpay
from api.filters.booking_filters import *
from api.models import *
from api.tasks import *
from api.utils.paginator import CustomPagination
from api.v1.bookings.serializers import *
from django.db import transaction
from django.db.models import Q
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
from decimal import Decimal


@api_view(['POST'])
def start_payment(request):

    with transaction.atomic():
        contact_persons_data = request.data.pop('contact_persons', [])

        booking_amount = request.data['booking_amount']
        package = request.data['package']

        # setup razorpay client this is the client to whome user is paying money that's you
        client = razorpay.Client(auth=(RAZOR_PUBLIC_KEY,RAZOR_SECRET_KEY))

        # print(client)

        # create razorpay order
    
        payment = client.order.create({"amount": int(booking_amount) * 100, 
                                    "currency": "INR", 
                                    "payment_capture": "1"})

        # print(payment)

        serializer = BookingCreateSerializer(data=request.data)

        if serializer.is_valid():
            print("hi1")
            instance = serializer.save()
            print(instance)
        else:
            print("Serializer errors:", serializer.errors)


        print("hi2")

        contact_serializer = ContactPersonSerializer(data=contact_persons_data,many=True)
        if contact_serializer.is_valid():
            contact_serializer.save(booking_id=instance.id)
        else:
            print("Serializer errors:", contact_serializer.errors)

        
        AgentTransactionSettlement.objects.create(package_id=request.data['package'],
                                                  booking_id=instance.id,
                                                  agent_id=34)


        # order = Booking.objects.create(package_id=package, 
        #                             booking_amount=booking_amount, 
        #                             payment_id=payment['id'])

        # serializer = BookingSerializer(order)

        

        data = {
            "payment": payment,
            "order": serializer.data
        }
        return Response(data)




class CustomerBookingListView(ListAPIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    serializer_class = BookingSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['user__username','booking_id'] 
    filterset_class = BookingFilter
    
    def get_queryset(self):
        today_date = datetime.now().date()

        queryset = Booking.objects.filter(user=self.kwargs['user_id'],
                                          is_trip_completed=0,
                                          tour_date__gt=today_date,
                                          booking_status__in=["SUCCESSFUL","REFUNDED REQUESTED"]).order_by("-id")
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
        


class CustomerBookingHistoryListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = BookingSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['user__username','booking_id'] 
    filterset_class = BookingFilter
    
    def get_queryset(self):
        queryset = Booking.objects.filter(
            Q(user=self.kwargs['user_id'],),
            Q(is_trip_completed=True) | Q(booking_status__in=["FAILED", "REFUNDED"])
        ).order_by("-id")
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

class CustomerBookingDetailsView(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    serializer_class = BookingSerializer


    def get_object(self):
        object_id = self.kwargs.get('object_id')
        return Booking.objects.get(object_id=object_id)

    def get(self, request, *args, **kwargs):
        try:

            instance = self.get_object()
            serializer = self.serializer_class(instance,context={'request': request})

            return Response({
                    "status": "success",
                    "message": "Listed successfully",
                    "statusCode": status.HTTP_200_OK,
                    "results": serializer.data,
                }, status=status.HTTP_200_OK)
            
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def put(self, request, *args, **kwargs):
        try:
            object_id = kwargs.get('object_id')
            instance = Booking.objects.get(object_id=object_id)
            
            if not instance:
                return Response({"message": "Booking object not found"}, status=status.HTTP_404_NOT_FOUND)

            # Deserialize and save the updated instance
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                if instance.booking_status == 'REFUNDED REQUESTED':
                    transaction_data = {"booking":instance,
                                        "user_id":request.user.id,
                                        "package":instance.package,
                                        "refund_status":"PENDING"}
                    UserRefundTransaction.objects.create(**transaction_data)

                subject = "Request for Cancellation"
                message = f'Cancellation Received for booking {instance.booking_id}'
                email = instance.user.email
                send_email.delay(subject,message,email)

                return Response({"message": "Booking Cancelled Successfully",
                                 "status": "success",
                                 "statusCode": status.HTTP_200_OK}, status=status.HTTP_200_OK)
            else:
                return Response({ "data": serializer.errors,
                                "message": "Something went wrong",
                                "status": "error",
                                "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        except Booking.DoesNotExist:
            return Response({"message": "Booking object not found",
                             "status": "error",
                            "statusCode": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def post(self, request, *args, **kwargs):
        try:

            with transaction.atomic():
                # contact_persons_data = request.data.pop('contact_persons', [])
                
                serializer = BookingCreateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()

                # if serializer.is_valid():
                #     instance = serializer.save()
                
                   
                
                # else:
                #     error_messages = ", ".join([", ".join(errors) for field, errors in serializer.errors.items()])
                #     return Response({ 'status': 'error', 'message': error_messages,
                #                         'statusCode': status.HTTP_400_BAD_REQUEST },
                #                         status=status.HTTP_400_BAD_REQUEST)

                # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                # contact_serializer = ContactPersonSerializer(data=contact_persons_data, many=True)
                # contact_serializer.is_valid(raise_exception=True)
                # contact_serializer.save(booking_id=instance.id)
                # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                
                # contact_serializer = ContactPersonSerializer(data=contact_persons_data,many=True)

                # if contact_serializer.is_valid():
                #     contact_serializer.save(booking_id=instance.id)
                # else:
                #     error_messages = ", ".join([", ".join(errors) for field, errors in serializer.errors.items()])
                #     return Response({ 'status': 'error', 'message': error_messages,
                #                         'statusCode': status.HTTP_400_BAD_REQUEST },
                #                         status=status.HTTP_400_BAD_REQUEST)
                

                AgentTransactionSettlement.objects.create(package_id=instance.package_id,
                                                  booking=instance,
                                                  agent_id=instance.package.agent_id)
                

                return Response({"message":"Booking created successfully",
                                "status": "success",
                                "statusCode": status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)

                
                
        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CustomerBookingUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = BookingCreateSerializer

    def put(self, request, *args, **kwargs):
        try:
            contact_persons_data = request.data.pop('contact_persons', [])
            object_id = kwargs.get('object_id')
            instance = Booking.objects.get(object_id=object_id)
            
            if not instance:
                return Response({"message": "Booking object not found", "status": "error",
                            "statusCode": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)

            # Deserialize and save the updated instance
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                if bool(contact_persons_data):
                    contact_serializer = ContactPersonSerializer(data=contact_persons_data, many=True)
                    contact_serializer.is_valid(raise_exception=True)
                    contact_serializer.save(booking_id=instance.id)

            
                return Response({"message": "Booking Updated Successfully",
                                 "status": "success",
                                 "statusCode": status.HTTP_200_OK}, status=status.HTTP_200_OK)
            else:
                return Response({ "data": serializer.errors,
                                "message": "Something went wrong",
                                "status": "error",
                                "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        
        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentBookingListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = BookingSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['user__first_name','user__username','booking_id','package__title'] 
    filterset_class = BookingFilter
    
    def get_queryset(self):
        
        queryset = Booking.objects.filter(package__agent_id=self.kwargs['agent_id']).order_by("-id")
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
    
        
        

class AgentBookingDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = BookingSerializer


    def get_object(self):
        object_id = self.kwargs.get('object_id')
        return Booking.objects.get(object_id=object_id)

    def get(self, request, *args, **kwargs):
        try:

            instance = self.get_object()
            serializer = self.serializer_class(instance,context={'request': request})

            return Response({
                    "status": "success",
                    "message": "Listed successfully",
                    "statusCode": status.HTTP_200_OK,
                    "results": serializer.data,
                }, status=status.HTTP_200_OK)
            
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AgentTransactionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AgentTransactionSettlementDetailSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['package__title','booking__user__username','transaction_id'] 
    filterset_class = AgentTransactionSettlementFilter
    
    def get_queryset(self):
       
        queryset = AgentTransactionSettlement.objects.filter(agent_id=self.kwargs['agent_id']).order_by("-id")
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
        
        

class AgentTransactionDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AgentTransactionSettlementDetailSerializer


    def get_object(self):
        object_id = self.kwargs.get('object_id')
        return AgentTransactionSettlement.objects.get(object_id=object_id)

    def get(self, request, *args, **kwargs):
        try:

            instance = self.get_object()
            serializer = self.serializer_class(instance)

            return Response({
                    "status": "success",
                    "message": "Listed successfully",
                    "statusCode": status.HTTP_200_OK,
                    "results": serializer.data,
                }, status=status.HTTP_200_OK)
            
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdvanceAmountPercentageSettingListView(APIView):
    """
      Returns the advance-amount-percentage-list 
    
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


   
    def get(self, request, *args, **kwargs):
        try:
            queryset = AdvanceAmountPercentageSetting.objects.values('id','category','category__title','percentage')

            category_id = self.request.GET.get('category_id')

            if category_id:
                queryset = queryset.filter(category=category_id)

            return Response({"results":queryset,
                             "message": "Listed sucessfully",
                            "status": "success",
                            "statusCode": status.HTTP_200_OK}, status=status.HTTP_200_OK)
        
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WelcomeView(APIView):
    

    def get(self, request, *args, **kwargs):
        subject = "Request for Cancellation"
        message = f'Cancellation Received for booking abc'
        print("z1")
        send_email.delay(subject,message,'lenate.j@flycatchtech.com')
        print("z2")
        return Response("checking celery")
    

class BookingCalculationsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, *args, **kwargs):
        try:

            pricing_id = self.request.GET.get('pricing_id',None)

            print(pricing_id)

            pricing = Pricing.objects.get(id=pricing_id)

            booking = Booking.objects.get(object_id=self.kwargs['object_id'])

            adult_per_rate = pricing.adults_rate
            child_per_rate = pricing.child_rate
            infant_per_rate = pricing.infant_rate

            print(booking)

            adult_count = booking.adult
            child_count  = booking.child
            infant_count = booking.infant

            full_amount_payment = (adult_per_rate * adult_count) + (child_per_rate * child_count) + (infant_per_rate * infant_count)
            partial_payment_percentage = AdvanceAmountPercentageSetting.objects.first().percentage
            partial_payment_amount = Decimal(full_amount_payment) * Decimal(partial_payment_percentage) / 100
            results = {
                            "adult_per_rate": adult_per_rate,
                            "child_per_rate": child_per_rate,
                            "infant_per_rate": infant_per_rate,
                            "adult_count":adult_count,
                            "child_count":child_count,
                            "infant_count":infant_count,
                            "full_amount_payment":full_amount_payment,
                            "partial_payment_percentage":partial_payment_percentage,
                            "partial_payment_amount":partial_payment_amount

                        }

            return Response({"results":results,
                            "message":"Listed successfully",
                            "status": "success",
                            "statusCode": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    
        except Exception as error_message:
            response_data = {"message": f"Something went wrong : {error_message}",
                            "status": "error",
                            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}  
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)