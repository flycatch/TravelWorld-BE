"""
This module defines core model classes used throughout the application.

- **BaseModel:** An abstract base class providing common fields for tracking creation,
  updation, status, and user management.
- **BaseUser:** An abstract base user class likely extended by specific user models
  (e.g., Agent, User). It inherits from Django's `AbstractBaseUser` and `PermissionsMixin`,
  providing basic user authentication functionalities. It has fields for name, phone,
  unique username, status, staff status, and timestamps. It defines a custom user manager
  using `CustomUserManager`.
- **AuditFields:** Another abstract base class providing fields for automatic tracking of
  creation and update timestamps.

These model classes provide a foundation for building upon in the application's models
and ensuring consistency in tracking creation, modification, and user management aspects.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from api.managers import CustomUserManager


class BaseModel(models.Model):
    """
    Abstract base model for tracking creation, updation, and status.

    This abstract model provides common fields for tracking the creation and update times
    of inherited models, as well as the object's current status (active or inactive).
    It serves as a foundation for building upon in the application's models, ensuring
    consistency in tracking these aspects.

    Attributes:
        updated_on (DateTimeField): The date and time the object was last updated
            (automatically updated on save).
        created_on (DateTimeField): The date and time the object was created
            (automatically set on creation).
        status (CharField): The current status of the object
            (choices are 'active' or 'inactive').
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]
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


class BaseUser (AbstractBaseUser,PermissionsMixin):
    """
    Abstract base user class with authentication functionalities.

    This class inherits from Django's `AbstractBaseUser` and `PermissionsMixin` to provide
    basic user authentication functionalities. It includes fields for user names, phone number,
    unique username (likely used for login), staff status, and timestamps. It defines a custom
    user manager (`CustomUserManager`) that might handle specific user creation or
    authentication logic.

    This class serves as a base for extending specific user models (e.g., Agent, Customer)
    within the application.

    Attributes:
        first_name (CharField): User's first name (optional).
        last_name (CharField): User's last name (optional).
        phone (CharField): User's phone number (optional).
        unique_username (CharField): Unique username used for login.
        status (CharField): User's current status (active or inactive).
        is_staff (BooleanField): Whether the user is a staff member with administrative privileges.
        updated_on (DateTimeField): Last updated date and time
            (automatically updated on save, can be null).
        created_on (DateTimeField): Creation date and time
            (automatically set on creation, can be null).
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
    ]

    first_name = models.CharField(_("First Name"), max_length=150, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    unique_username = models.CharField(
        _("Username"), max_length=256, null=True, blank=True, unique=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    is_staff = models.BooleanField(default=False)
    updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'unique_username'
    class Meta:
        """
        verbose_name (str): A human-readable name for the model, used in the admin interface.
        verbose_name_plural (str): A human-readable plural name for the model, used in the
            admin interface.
        """
        verbose_name = _('Super Admin')
        verbose_name_plural = _('Super Admin')

    def __str__(self):
        """
        Returns a string representation of the super admin's unique username.
        """
        return self.unique_username


class AuditFields(models.Model):
    """
    Abstract model for tracking audit fields.

    Attributes:
        created_on (datetime): Added date of the object.
        updated_on (datetime): Last updated date of the object.
    """
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        """
        Meta options for the AuditFields model.

        Attributes:
            abstract (bool): Indicates that this model is abstract
            and should not be created in the database.
        """
        abstract = True
