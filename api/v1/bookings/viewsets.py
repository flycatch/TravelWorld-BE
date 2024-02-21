import razorpay
from api.filters.booking_filters import *
from api.models import *
from api.tasks import *
from api.utils.paginator import CustomPagination
from api.v1.bookings.serializers import *
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
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = BookingSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['customer__first_name'] 
    filterset_class = BookingFilter
    
    def get_queryset(self):
        try:
            queryset = Booking.objects.filter(user=self.kwargs['user_id']).order_by("-id")
            return queryset
        
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CustomerBookingDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = BookingSerializer


    def get_object(self):
        object_id = self.kwargs.get('object_id')
        return Booking.objects.get(object_id=object_id)

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
                    Transaction.objects.create(**transaction_data)

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
        


class AgentBookingListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = BookingSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['user__first_name','user__username','booking_id','package__title'] 
    filterset_class = BookingFilter
    
    def get_queryset(self):
        try:
            queryset = Booking.objects.filter(package__agent_id=self.kwargs['agent_id']).order_by("-id")
            return queryset
        
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
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

class AgentTransactionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AgentTransactionSettlementDetailSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,SearchFilter]
    search_fields = ['package__title','booking__user__username','transaction_id'] 
    filterset_class = AgentTransactionSettlementFilter
    
    def get_queryset(self):
        try:
            queryset = AgentTransactionSettlement.objects.filter(agent_id=self.kwargs['agent_id']).order_by("-id")
            return queryset
        
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
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