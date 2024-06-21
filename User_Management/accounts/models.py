import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from django_ckeditor_5.fields import CKEditor5Field
from accounts.common.models import BaseModel, BaseUser, AuditFields
from accounts.utils.choices import *
from simple_history.models import HistoricalRecords
from django.utils.safestring import mark_safe
from accounts.utils.functions import compress_image

class User(BaseUser):
    user_uid = models.CharField(max_length=256, null=True, blank=True, verbose_name='User UID')
    profile_image = models.ImageField(upload_to='profile_images/user/', null=True, blank=True)
    username = models.CharField(max_length=256, null=True, blank=True, unique=True)
    email = models.EmailField(unique=True,null=True, blank=True)
    mobile = models.CharField(unique=True,max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.user_uid if self.user_uid else self.username

    def save(self, *args, **kwargs):
        if self.profile_image:
            self.profile_image = compress_image(self.profile_image)
        super(User, self).save(*args, **kwargs)


class Agent(BaseUser):
    """
    Model representing an Agent user in the system.

    This model extends the BaseUser model and adds additional fields specific to agents.
    Agents can be in different stages ('pending', 'approved', 'rejected') 
    based on their application process. They can also have their bank account 
    verification status set ('pending', 'approved', 'rejected').

    **Fields:**

    * agent_uid (CharField): Unique identifier for the agent (automatically generated
        and non-editable).
    * profile_image (ImageField, optional): Image representing the agent's profile.
    * username (CharField, unique): Username for agent login (can be blank).
    * email (EmailField, unique): Email address of the agent (can be blank).
    * agent_name (CharField): Full name of the agent.
    * company_id (CharField, optional): Registration number of the agent's company (if any).
    * company_name (CharField, optional): Name of the agent's company (if any).
    * company_site (CharField, optional): Website of the agent's company (if any).
    * message (TextField, optional): Message from the agent.
    * stage (CharField, choices=STAGES_CHOICES, default='pending'): Current stage of the agent's 
        application process.
    * account_verification_status (CharField, choices=ACCOUNT_VERIFICATION_CHOICES, default='pending')
        Verification status of the agent's bank account.

    **Meta:**

    * verbose_name: 'Agent' (singular)
    * verbose_name_plural: 'Agents' (plural)

    **Methods:**

    * __str__(): Returns the agent's unique identifier (agent_uid).
    """
    STAGES_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    ACCOUNT_VERIFICATION_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
 
    agent_uid = models.CharField(max_length=10, unique=True, editable=False, verbose_name='Agent UID')
    profile_image = models.ImageField(upload_to='profile_images/agent/', null=True, blank=True)
    username = models.CharField(max_length=256, null=True, blank=True, unique=True)
    email = models.EmailField(unique=True,null=True, blank=True)
    agent_name = models.CharField(_("Agent Name"), max_length=150, blank=True, null=True)
    company_id = models.CharField(_("Company Registration Number"), max_length=150, blank=True, null=True)
    company_name = models.CharField(_("Company Name"), max_length=150, blank=True, null=True)
    company_site = models.CharField(_("Company Website"), max_length=150, blank=True, null=True)
    message = models.TextField(_("Message"), blank=True, null=True)
    stage = models.CharField(
        max_length=20,
        choices=STAGES_CHOICES,
        default='pending',
        verbose_name=_('Stage'),
    )
    account_verification_status = models.CharField(
        max_length=20,
        choices=ACCOUNT_VERIFICATION_CHOICES,
        default='pending',
        verbose_name=_('Bank Account Verification'),
    )

    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return self.agent_uid

    def save(self, *args, **kwargs):
        if self.profile_image:
            self.profile_image = compress_image(self.profile_image)
        super(Agent, self).save(*args, **kwargs)


class AgentBankDetails(BaseModel):
    agent = models.OneToOneField(
        Agent, on_delete=models.CASCADE, related_name='bank_details')
    account_holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255, verbose_name='Bank Name',
                                 null=True, blank=True)
    account_number = models.CharField(max_length=255, verbose_name='Account Number')
    ifsc_code = models.CharField(max_length=255, verbose_name='IFSC Code')
    cancelled_cheque = models.ImageField(
        upload_to='cancelled_cheques/', null=True, default=None, blank=True,
        verbose_name="Cancelled Cheque")

    class Meta:
        verbose_name = 'Agent Bank Details'
        verbose_name_plural = 'Agent Bank Details'