from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager.
    """
    def create_user(self, unique_username, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        if not unique_username:
            raise ValueError(_('The Email must be set'))
        user = self.model(unique_username=unique_username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, unique_username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user( unique_username, password, **extra_fields)