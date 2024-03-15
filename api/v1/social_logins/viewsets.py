from django.shortcuts import redirect
from random import SystemRandom
from typing import Any, Dict
from urllib.parse import urlencode
from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework.views import APIView
import jwt
import requests
from attrs import define
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
from rest_framework import status
# from styleguide_example.core.exceptions import ApplicationError
from rest_framework import serializers
from api.models import *
from rest_framework.authtoken.models import Token
from api.backends import ModelBackend,BaseUserModelBackend
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from api.v1.social_logins.serializers import *

@define
class GoogleRawLoginCredentials:
    client_id: str
    client_secret: str
    project_id: str


@define
class GoogleAccessTokens:
    id_token: str
    access_token: str

    def decode_id_token(self) -> Dict[str, str]:
        id_token = self.id_token
        decoded_token = jwt.decode(jwt=id_token, options={"verify_signature": False})
        return decoded_token



def google_raw_login_get_credentials() -> GoogleRawLoginCredentials:
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
    project_id = settings.GOOGLE_OAUTH2_PROJECT_ID

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in env.")

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_PROJECT_ID missing in env.")

    credentials = GoogleRawLoginCredentials(client_id=client_id, client_secret=client_secret, project_id=project_id)

    return credentials

class ApplicationError(Exception):
    def __init__(self, message, extra=None):
        super().__init__(message)

        self.message = message
        self.extra = extra or {}


class GoogleRawLoginFlowService:
    
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    def __init__(self):
        self._credentials = google_raw_login_get_credentials()

    @staticmethod
    def _generate_state_session_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
        # This is how it's implemented in the official SDK
        rand = SystemRandom()
        state = "".join(rand.choice(chars) for _ in range(length))
        return state

    def _get_redirect_uri(self):
        domain = settings.DJANGO_BASE_BACKEND_URL
        redirect_uri = f"{domain}/api/v1/google/callback"
        return redirect_uri

    def get_authorization_url(self):
        redirect_uri = self._get_redirect_uri()

        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            # "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }

        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"

        return authorization_url

    def get_tokens(self, *, code: str) -> GoogleAccessTokens:
        redirect_uri = self._get_redirect_uri()

        # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        if not response.ok:
            raise ApplicationError("Failed to obtain access token from Google.")

        tokens = response.json()
        google_tokens = GoogleAccessTokens(id_token=tokens["id_token"], access_token=tokens["access_token"])

        return google_tokens

    def get_user_info(self, *, google_tokens: GoogleAccessTokens) -> Dict[str, Any]:
        access_token = google_tokens.access_token
        # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#callinganapi
        response = requests.get(self.GOOGLE_USER_INFO_URL, params={"access_token": access_token})

        if not response.ok:
            ...
            # raise ApplicationError("Failed to obtain user info from Google.")

        return response.json()



class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()


class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        try:
            google_login_flow = GoogleRawLoginFlowService()

            authorization_url= google_login_flow.get_authorization_url()
            return redirect(authorization_url)


            # request.session["google_oauth2_state"] = state

            # return Response({
            #         "status": "success",
            #         "message": "Listed successfully",
            #         "statusCode": status.HTTP_200_OK,
            #         "results": authorization_url,
            #     }, status=status.HTTP_200_OK)
        
        except Exception as error_message:
                response_data = {"message": f"Something went wrong: {error_message}",
                                "status": "error",
                                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
from google.oauth2 import id_token
from google.auth.transport import requests
import google.auth

class GoogleLoginApi(PublicApi):


    def get(self, request, *args, **kwargs):
        try:
            input_serializer = InputSerializer(data=request.GET)
            input_serializer.is_valid(raise_exception=True)

            validated_data = input_serializer.validated_data

            code = validated_data.get("code")
            error = validated_data.get("error")
            # state = validated_data.get("state")

            print("hi1")
            print(code)
            print(error)

            if error is not None:
                return Response({ "message": error,
                                "status": "error",
                                "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            if code is None :
                return Response({ "message": "Code and state are required.",
                                "status": "error",
                                "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            # session_state = request.session.get("google_oauth2_state")

            # if session_state is None:
            #     return Response({ "message": "CSRF check failed",
            #                     "status": "error",
            #                     "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
                

            # del request.session["google_oauth2_state"]

            # if state != session_state:
            #     return Response({ "message": "CSRF check failed.",
            #                     "status": "error",
            #                     "statusCode": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            
            print("helo")
            google_login_flow = GoogleRawLoginFlowService()
            print("a0")
            print(google_login_flow)

            # google_tokens = google_login_flow.get_tokens(code=code)

            # print("a1")
            # print(google_tokens)

            # id_token_decoded = google_tokens.decode_id_token()
            # idinfo = id_token.verify_oauth2_token(code, requests.Request(), settings.GOOGLE_OAUTH2_CLIENT_ID)
            idinfo = id_token.verify_oauth2_token(
                code,
                google.auth.transport.requests.Request(),
                settings.GOOGLE_OAUTH2_CLIENT_ID
            )
            print(idinfo)

            # user_info = google_login_flow.get_user_info(google_tokens=code)

            # print(user_info)

            user_email = user_info["email"]
            
            print("z1")
            print(user_email)

            # Search for the user with email id
            user = User.objects.filter(email=user_email).first()

            # if user does not exists
            if not user:
                # create a user 
                user = User.objects.create(
                        email=user_email,
                        first_name=user_info["name"],
                
                )    

            # Get or create a token
            token, created = Token.objects.get_or_create(user=user)
            login(request, user,backend='api.backends.BaseUserModelBackend')

           
            return Response({'status': 'success', 'message': 'Login Successful', 
                             "user_info": user_info,
                             'token': token.key, 'statusCode': status.HTTP_200_OK},
                             status=status.HTTP_200_OK)
        
        except Exception as error_message:
                response_data = {"message": f"Something went wrong: {error_message}",
                                "status": "error",
                                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# from library.sociallib import facebook



class FacebookRawLoginFlowService:
  
    FACEBOOK_AUTH_URL = "https://graph.facebook.com/oauth/access_token"
    
    def get_authorization_url(self):

        params = {
            "client_id": settings.FACEBOOK_CLIENT_ID,
            "client_secret":settings.FACEBOOK_SECRET_ID,
            "redirect_uri": "http://127.0.0.1:8000/api/v1/facebook/callback",
            "grant_type":"client_credentials"
        }

        query_params = urlencode(params)
        authorization_url = f"{self.FACEBOOK_AUTH_URL}?{query_params}"
        print(authorization_url)

        return authorization_url


class FacebookLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        facebook_login_flow = FacebookRawLoginFlowService()
        authorization_url= facebook_login_flow.get_authorization_url()
        print("a1")
        return redirect(authorization_url)
    

@csrf_exempt
@api_view(['POST'])
def fb_login(request):

    print("hello")
    print(request)

    ...

    # user_data = facebook.Facebook.validate(auth_token)
    # print(user_data)
    # data = json.loads(request.body)
    token = request.data['access_token'] 
    print(token)
    # user_id = data['userID']
    # email = data['email']
    # user_role = data['user_role']
    # if user_role:            
    #     user_role = [i[0] for i in choices.USER_ROLE_CHOICES if i[1] == user_role][0]
    # # print(token)

    # authorization_header = request.META.get("HTTP_AUTHORIZATION")
    # print("l5.10")
    # print(authorization_header)
    # id_token = authorization_header.split(" ").pop()
    # print("l6")
    # print(id_token)
    # data = auth.verify_id_token(id_token)
    # print(data)
    # try:
    #     print("l7")
    #     data = auth.verify_id_token(id_token)
    #     print(data)

    response = requests.get(' https://graph.facebook.com/me?access_token='+str(token))
    print(response.json())
    # if response.status_code == 200:
        # ...