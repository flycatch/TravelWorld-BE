from api.models import User
from api.tasks import *
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from api.v1.agent.serializers import PasswordResetConfirmSerializer
from api.v1.user.serializers import UserSerializer, UserLoginSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    http_method_names = ['get','put']

    def get_queryset(self):
        return self.queryset.filter(pk=self.request.user.pk)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print('ok')
            return Response({'status': 'success', 'message': 'User updated successfully',
                             'data': serializer.data, 'statusCode': status.HTTP_200_OK},
                             status=status.HTTP_200_OK)
        except serializers.ValidationError as e:
            print('hi')
            # Extract error messages from the serializer's errors attribute
            error_messages = ", ".join([", ".join(errors) for field, errors in serializer.errors.items()])
            return Response({'status': 'error', 'message': error_messages,
                             'statusCode':status.HTTP_400_BAD_REQUEST},
                             status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print('hiii')
            # Return appropriate status code for other exceptions
            return Response({'status': 'error', 'message': str(e),
                             'statusCode': status.HTTP_500_INTERNAL_SERVER_ERROR},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({'status': 'success','message': 'User registered successfully',
                             'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            error_messages = ", ".join([", ".join(errors) for field, errors in serializer.errors.items()])
            return Response({ 'status': 'error', 'message': error_messages,
                             'statusCode': status.HTTP_400_BAD_REQUEST },
                             status=status.HTTP_400_BAD_REQUEST)


class UserLoginViewset(viewsets.ModelViewSet):
    serializer_class = UserLoginSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            response_data = serializer.save()
            return Response({'status': 'success', 'message': 'Login Successful', 
                             'token': response_data, 'statusCode': status.HTTP_200_OK},
                             status=status.HTTP_200_OK)
        except Exception as error_message:
            return Response({'status': 'error', 'message': "Invalid username or email, or incorrect password",
                             'statusCode': status.HTTP_400_BAD_REQUEST},
                             status=status.HTTP_400_BAD_REQUEST)


class UserForgotPassword(APIView):
    def post(self, request):
        
        try:
            email = request.data.get('email')
            if not email:
                return Response({'message': 'Please provide an email address',
                                 "status": "error",
                                "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'message': 'User with that email address does not exist',
                                 "status": "error",
                                "statusCode": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
            
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(str(user.id).encode())
            reset_url = f"{DEFAULT_BASE_URL_USER_FRONTEND}/reset-password?uidb64={uidb64}&token={token}"

          
            send_email.delay('Reset your password',
                             f'Please click the following link to reset your password: {reset_url}',
                             email
                             )
            return Response({'message': 'Password reset email and verification code has been sent.',
                              "status": "success",
                            "statusCode": status.HTTP_200_OK})
    
        except Exception as error_message:
            response_data = {"message": f"Something went wrong: {error_message}",
                             "status": "error",
                             "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserCustomPasswordResetConfirmView(APIView):
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
                    user = User.objects.get(pk=uid)

                except User.DoesNotExist:
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