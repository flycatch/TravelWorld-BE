# api/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from api.models import *

class BaseUserModelBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, model=None, **kwargs):
        UserModel = model
        user=None

        if email:
            try:
                user = UserModel.objects.get(email=email)

            except UserModel.DoesNotExist:
                pass

        if not user and username:
            print(request)
            try:
                user = UserModel.objects.get(username=username)

            except UserModel.DoesNotExist:
                user = BaseUser.objects.get(unique_username=username)
                pass

        if user and user.check_password(password):
            return user

        return None
