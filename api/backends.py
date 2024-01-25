# api/backends.py

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class BaseUserModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        print(UserModel)
        try:
            print(username)
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            print(1)
            print(user)
            return user
        return None
