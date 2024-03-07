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
    # API_URI = reverse_lazy("api:google-oauth2:login-raw:callback-raw")
    # print(API_URI)

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

    # def _get_redirect_uri(self):
    #     # domain = settings.BASE_BACKEND_URL
    #     api_uri = self.API_URI
    #     redirect_uri = "http://127.0.0.1:8000/api/callback"
    #     return redirect_uri

    def get_authorization_url(self):
        # redirect_uri = self._get_redirect_uri()

        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": "http://127.0.0.1:8000/api/v1/google/callback",
            "scope": " ".join(self.SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }

        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"

        return authorization_url, state

    def get_tokens(self, *, code: str) -> GoogleAccessTokens:
        # redirect_uri = self._get_redirect_uri()

        # Reference: https://developers.google.com/identity/protocols/oauth2/web-server#obtainingaccesstokens
        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": "http://127.0.0.1:8000/api/v1/google/callback",
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
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state


        return redirect(authorization_url)
    

class GoogleLoginApi(PublicApi):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        try:
            input_serializer = self.InputSerializer(data=request.GET)
            input_serializer.is_valid(raise_exception=True)

            validated_data = input_serializer.validated_data

            print(validated_data)
            code = validated_data.get("code")
            error = validated_data.get("error")
            state = validated_data.get("state")

            if error is not None:
                return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

            if code is None or state is None:
                return Response({"error": "Code and state are required."}, status=status.HTTP_400_BAD_REQUEST)

            session_state = request.session.get("google_oauth2_state")

            if session_state is None:
                return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)

            del request.session["google_oauth2_state"]

            if state != session_state:
                return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)

            google_login_flow = GoogleRawLoginFlowService()

            google_tokens = google_login_flow.get_tokens(code=code)

            id_token_decoded = google_tokens.decode_id_token()
            user_info = google_login_flow.get_user_info(google_tokens=google_tokens)

            print(user_info)

            user_email = id_token_decoded["email"]
            
            print("z1")
            print(user_email)

            # Search for the user with email id
            user = User.objects.filter(email=user_email).first()

            # if user does not exists
            if not user:
                # create a user 
                user = User.objects.create(
                        email=user_email,
                        first_name=id_token_decoded["name"],
                
                )    

            # Get or create a token
            token, created = Token.objects.get_or_create(user=user)

            print(token,created)

            login(request, user,backend='api.backends.BaseUserModelBackend')

            # result = {
            #     "id_token_decoded": id_token_decoded,
            #     "user_info": user_info,
            #     "message":'Successfull Login.'
            # }

            return Response({'status': 'success', 'message': 'Login Successful', 
                             "user_info": user_info,
                             'token': token.key, 'statusCode': status.HTTP_200_OK},
                             status=status.HTTP_200_OK)
        
        except Exception as error_message:
                response_data = {"message": f"Something went wrong: {error_message}",
                                "status": "error",
                                "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR}
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)