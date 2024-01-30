from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.common.library import encode


class BaseModel(models.Model):
    """
    Abstract base model for tracking.

    Atribs:
        creator(obj): Creator of the object
        updater(obj): Updater of the object
        created_on(datetime): Added date of the object
        updated_on(datetime): Last updated date of the object
    """

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
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    class Meta:
        """Meta class for the above model."""

        abstract = True
        ordering = ("-created_on",)

    @property
    def idencode(self):
        """To return encoded id."""
        return encode(self.id)


class BaseUser(AbstractUser):
    first_name = models.CharField(_("First Name"), max_length=150, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = _('Base User')
        verbose_name_plural = _('Base Users')

    def __str__(self):
        return self.username
    