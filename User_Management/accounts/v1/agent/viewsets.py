from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.filters import SearchFilter

from accounts.models import Agent, AgentBankDetails
from accounts.tasks import *
from accounts.v1.agent.serializers import (AgentLoginSerializer, AgentSerializer,
                                      PasswordResetConfirmSerializer,
                                      AgentBankDetailsSerializer)


class AgentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operation on agent's profile.

    This viewset provides methods to:

    * **GET /agents/**: Retrieve the profile of the currently authenticated agent.
    * **POST /agents/**: Create new agent.
    * **PUT /agents/**: Update the profile of the currently authenticated agent.
    * **DELETE /agents/**: delete agent profile.

    Authentication is required for all operations. Only PUT requests are allowed for updating the agent profile.

    **Permissions:**

    * IsAuthenticated: Only authenticated users can access this viewset.

    **Authentication:**

    * TokenAuthentication: Authentication is done using token-based authentication.

    **Returns:**

    * A JSON response with status information, message, and data on success.
    * A JSON response with error messages and status code on failure.
    """
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    http_method_names = ['get','put']

    def get_queryset(self):
        """
        Filters the queryset to only include the currently authenticated agent.
        """
        return self.queryset.filter(pk=self.request.user.pk)

    def update(self, request, *args, **kwargs):
        """
        Updates the profile of the currently authenticated agent.

        Handles validation errors and other exceptions.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'status': 'success', 'message': 'Agent updated successfully',
                             'data': serializer.data, 'StatusCode': status.HTTP_200_OK},
                             status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            # Extract error messages from the serializer's errors attribute
            error_messages = ", ".join([", ".join(errors) for field, errors in serializer.errors.items()])
            return Response({'status': 'error', 'message': error_messages,
                             'statusCode':status.HTTP_400_BAD_REQUEST},
                             status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'error', 'message': str(e),
                             'statusCode': status.HTTP_400_BAD_REQUEST},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'status': 'success','message': 'Agent registered successfully',
                             'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            error_messages = ", ".join([", ".join(errors) for field, errors in serializer.errors.items()])
            return Response({ 'status': 'error', 'message': error_messages,
                             'statusCode': status.HTTP_400_BAD_REQUEST },
                             status=status.HTTP_400_BAD_REQUEST)


class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = AgentLoginSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save()
            return Response({'status': 'success', 'message': 'Login successful',
                            'token': response_data, "statusCode": status.HTTP_200_OK},
                            status=status.HTTP_200_OK)
        except Exception as e:
            # Construct response with error message from the exception
            error_message = {'message': e.detail, 'status': 'error',
                             "statusCode": status.HTTP_404_NOT_FOUND}
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(APIView):
    def post(self, request):
        
        try:
            email = request.data.get('email')
            if not email:
                return Response({'message': 'Please provide an email address',
                                 "status": "error", "statusCode": status.HTTP_400_BAD_REQUEST},
                                 status=status.HTTP_400_BAD_REQUEST)

            try:
                user = Agent.objects.get(email=email)
            except Agent.DoesNotExist:
                return Response({'message': 'User with that email address does not exist',
                                 "status": "error", "statusCode": status.HTTP_404_NOT_FOUND},
                                status=status.HTTP_404_NOT_FOUND)
            
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(str(user.id).encode())
            reset_url = f"{DEFAULT_BASE_URL}/reset-password?uidb64={uidb64}&token={token}"

          
            send_email.delay('Reset your password',
                             f'Please click the following link to reset your password: {reset_url}',
                             email
                             )
            return Response({'message': 'Password reset email has been sent to your registered email address.',
                              "status": "success",
                            "statusCode": status.HTTP_200_OK})
    
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CustomPasswordResetConfirmView(APIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        try:

            uidb64 = request.GET.get('uidb64')
            token = request.GET.get('token')

            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():

                uidb64_bytes = force_bytes(uidb64)
                uid = urlsafe_base64_decode(uidb64).decode()
            
                try:
                    user = Agent.objects.get(pk=uid)

                except Agent.DoesNotExist:
                    return Response({'message': 'User with that email address does not exist',
                                    "status": "error",
                                    "statusCode": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
                
                if not default_token_generator.check_token(user, token):
                    return Response({'message': 'Invalid password reset link',
                                     "status": "error",
                                    "statusCode": status.HTTP_400_BAD_REQUEST}, status=400)

                # Set the user's password to the new password and save
                user.password=make_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'message': 'Password reset successfully',
                                 "status": "success",
                                "statusCode": status.HTTP_200_OK})
            
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


class AgentBankDetailsAPIView(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on Agent Bank Details.

    This viewset provides methods to list, create, update, and retrieve agent bank details.
    Authentication is required for all operations.

    **Permissions:**

    * List: Only authenticated agents can access their own bank details.
    * Create: Only authenticated agents can create their own bank details.
    * Update: Only authenticated agents can update their own bank details.

    **Methods:**

    * **GET /agent-bank-details/**: Retrieves a list of the current agent's bank details.
    * **POST /agent-bank-details/**: Creates new bank details for the current agent.
    * **PUT /agent-bank-details/<pk>/**: Updates an existing bank detail object.

    **Returns:**

    * A JSON response with status information and data on success.
    * A JSON response with error messages on failure.
    """
    queryset = AgentBankDetails.objects.all()
    serializer_class = AgentBankDetailsSerializer

    def list(self, request, *args, **kwargs):
        # Get the current logged-in agent's ID
        agent_id = request.user.agent.id
        # Filter queryset based on the current agent's ID
        queryset = self.queryset.filter(agent_id=agent_id)
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({"message": "Agent Bank Details Added Successfully",
                             "status": "success",
                             "statusCode": status.HTTP_201_CREATED},
                             status=status.HTTP_201_CREATED, headers=headers)
        except Exception:
            error_message = ", ".join([f"{field}: {', '.join(errors)}" for field, errors in serializer.errors.items()])
            return Response({"message": error_message,
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            #make account_verification_status to pending
            instance.agent.account_verification_status = 'pending'
            instance.agent.save()
            
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response({"message": "Agent Bank Details Updated Successfully",
                             "status": "success",
                             "statusCode": status.HTTP_200_OK})
        except Exception:
            error_message = ", ".join([f"{field}: {', '.join(errors)}" for field, errors in serializer.errors.items()])
            return Response({"message": f"Failed To Update Agent Bank Details: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class WelcomeView(APIView):
    

    def get(self, request, *args, **kwargs):
        subject = "Request for Cancellation"
        message = f'Cancellation Received for booking abc'
        send_email.delay(subject,message,'lenate.j@flycatchtech.com')
        return Response("checking celery")
    