from api.common.library import encode
from api.managers import CustomUserManager
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, AbstractUser,
                                        PermissionsMixin)
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Abstract base model for tracking.

    Atribs:
        creator(obj): Creator of the object
        updater(obj): Updater of the object
        created_on(datetime): Added date of the object
        updated_on(datetime): Last updated date of the object
    """

    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]
    # creator = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     default=None,
    #     null=True,
    #     blank=True,
    #     related_name="creator_%(class)s_objects",
    #     on_delete=models.SET_NULL,
    # )
    # updater = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     default=None,
    #     null=True,
    #     blank=True,
    #     related_name="updater_%(class)s_objects",
    #     on_delete=models.SET_NULL,
    # )
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    class Meta:
        """Meta class for the above model."""

        abstract = True
        ordering = ("-created_on",)

    @property
    def idencode(self):
        """To return encoded id."""
        return encode(self.id)


class BaseUser (AbstractBaseUser,PermissionsMixin):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]
    
    first_name = models.CharField(_("First Name"), max_length=150, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    unique_username = models.CharField(_("Username"), max_length=256, null=True, blank=True, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    is_staff = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = 'unique_username'
    class Meta:
        verbose_name = _('Base User')
        verbose_name_plural = _('Base Users')

    def __str__(self):
        return self.unique_username
    

class AuditFields(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True