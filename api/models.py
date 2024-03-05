import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from api.common.models import BaseModel, BaseUser, AuditFields
from api.utils.choices import *

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
    
   


class Agent(BaseUser):
    STAGES_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    agent_uid = models.CharField(max_length=10, unique=True, editable=False, verbose_name='Agent UID')
    profile_image = models.ImageField(upload_to='profile_images/agent/', null=True, blank=True)
    stage = models.CharField(
        max_length=20,
        choices=STAGES_CHOICES,
        default='pending',
        verbose_name=_('Stage'),
    )
    username = models.CharField(max_length=256, null=True, blank=True, unique=True)
    email = models.EmailField(unique=True,null=True, blank=True)
    agent_name = models.CharField(_("Agent Name"), max_length=150, blank=True,null=True)


    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return self.agent_uid

    #Generate unique agent id
    # def save(self, *args, **kwargs):
    #     if not self.agent_uid:
    #         last_agent = Agent.objects.order_by('-agent_uid').first()
    #         last_id = last_agent.agent_uid[4:] if last_agent else '0'
    #         new_id = str(int(last_id) + 1)
    #         self.agent_uid = f'EWAG{new_id}'

    #     if not self.unique_username:
    #         self.unique_username = f'{self.username}_{new_id}'

    #     super().save(*args, **kwargs)


class Country(BaseModel):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='country_images/', null=True, default=None, blank=True)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name

    def clean(self):
        # Check for uniqueness of country name (case-insensitive)
        country = Country.objects.filter(name__iexact=self.name).exclude(pk=self.pk)
        if country.exists():
            raise ValidationError({'name': f'Country with {self.name} already exists.'})

        # Check if the name contains only alphabetic characters
        if not self.name.replace(' ', '').isalpha():
            raise ValidationError(
                {'name': _('Country name should contain only alphabetic characters.')})


class State(BaseModel):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='state_country')
    thumb_image = models.ImageField(
        upload_to='state/thumb_images/',
        null=True, default=None, blank=True, verbose_name="Thumb Image")
    cover_img = models.ImageField(
        upload_to='state/cover_image/', 
        null=True, default=None, blank=True, verbose_name="Cover Image")

    class Meta:
        verbose_name = 'State'
        verbose_name_plural = 'States'

    def __str__(self):
        return self.name

    def clean(self):
        # Check for uniqueness of country name (case-insensitive)
        state = State.objects.filter(name__iexact=self.name,
                                     country=self.country).exclude(pk=self.pk)
        if state.exists():
            raise ValidationError({'name': f'{self.country} with {self.name} already exists.'})

        # Check if the name contains only alphabetic characters
        if not self.name.replace(' ', '').isalpha():
            raise ValidationError(
                {'name': _('State name should contain only alphabetic characters.')})


class City(BaseModel):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='city_state')
    thumb_image = models.ImageField(
        upload_to='city/thumb_images/',
        null=True, default=None, blank=True, verbose_name="Thumb Image")
    cover_img = models.ImageField(
        upload_to='city/cover_image/', 
        null=True, default=None, blank=True, verbose_name="Cover Image")

    class Meta:
        verbose_name = 'City'
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.name

    def clean(self):
        # Check for uniqueness of country name (case-insensitive)
        city = City.objects.filter(name__iexact=self.name, state=self.state).exclude(pk=self.pk)
        if city.exists():
            raise ValidationError({'name': f'{self.state} with {self.name} already exists.'})

        # Check if the name contains only alphabetic characters
        if not self.name.replace(' ', '').isalpha():
            raise ValidationError(
                {'name': _('City name should contain only alphabetic characters.')})


class PackageCategory(BaseModel):
    name = models.CharField(max_length=255)
    thumb_img = models.ImageField(
        upload_to='package/category/thumb_images/', 
        null=True, default=None, blank=True, verbose_name="Thumb Image")
    cover_img = models.ImageField(
        upload_to='package/category/cover_image/', 
        null=True, default=None, blank=True, verbose_name="Cover Image")

    class Meta:
        verbose_name = 'Tour Category'
        verbose_name_plural = 'Tour Category'

    def __str__(self):
        return self.name



class ActivityCategory(BaseModel):
    name = models.CharField(max_length=255)
    thumb_img = models.ImageField(
        upload_to='activity/category/thumb_images/', 
        null=True, default=None, blank=True, verbose_name="Thumb Image")
    cover_img = models.ImageField(
        upload_to='activity/category/cover_image/', 
        null=True, default=None, blank=True, verbose_name="Cover Image")

    class Meta:
        verbose_name = 'Activity Category'
        verbose_name_plural = 'Activity Category'

    def __str__(self):
        return self.name


class Activity(BaseModel):
    STAGES_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    TOUR_CLASS_CHOICE = [
        ('private', _('Private')),
        ('conducting', _('Conducting'))
    ]
    DURATION_CHOICE = [
        ('day', _('Day Night')),
        ('hour', _('Hours'))
    ]

    activity_uid = models.CharField(max_length=256, null=True, blank=True, verbose_name='Activity UID')
    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name='activity_agent')
    title = models.CharField(max_length=255)
    tour_class = models.CharField(
        max_length=20,
        choices=TOUR_CLASS_CHOICE,
        default='private',
        verbose_name='Tour Class'
    )
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='activity_country')
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='activity_state')
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='activity_city')
    category = models.ForeignKey(
        PackageCategory, on_delete=models.CASCADE,
        related_name='activity_category',
        blank=True, null=True)
    
    min_members = models.IntegerField(null=True, blank=True)
    max_members = models.IntegerField(null=True, blank=True)
    duration = models.CharField(
            max_length=20,
            choices=DURATION_CHOICE,
            default='day',
            verbose_name='Duration'
        )
    duration_day = models.IntegerField(verbose_name='Duration Days', null=True, blank=True)
    duration_night = models.IntegerField(verbose_name='Duration Nights', null=True, blank=True)
    duration_hour = models.IntegerField(verbose_name='Duration Hours', null=True, blank=True)
    pickup_point = models.CharField(max_length=255, blank=True, null=True,
                                    verbose_name='Pickup Point')
    pickup_time = models.DateTimeField(verbose_name='Pickup Time', blank=True, null=True)
    drop_point = models.CharField(max_length=255, blank=True, null=True,
                                  verbose_name='Drop Point')
    drop_time = models.DateTimeField(verbose_name='Drop Time', blank=True, null=True)

    stage = models.CharField(
        max_length=20,
        choices=STAGES_CHOICES,
        default='pending',
        verbose_name='Stage'
    )
    is_submitted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activity'

    def __str__(self):
        return self.activity_uid if self.activity_uid else self.title



class Package(BaseModel):
    STAGES_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    TOUR_CLASS_CHOICE = [
        ('private', _('Private')),
        ('conducting', _('Conducting'))
    ]
    DURATION_CHOICE = [
        ('day', _('Day Night')),
        ('hour', _('Hours'))
    ]

    package_uid = models.CharField(max_length=256, null=True, blank=True, verbose_name='Package UID')
    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name='package_agent')
    title = models.CharField(max_length=255)
    tour_class = models.CharField(
        max_length=20,
        choices=TOUR_CLASS_CHOICE,
        default='private',
        verbose_name='Tour Class'
    )
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='package_country')
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='package_state')
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='package_city')
    category = models.ForeignKey(
        PackageCategory, on_delete=models.CASCADE, related_name='package_category')
    min_members = models.IntegerField(null=True, blank=True)
    max_members = models.IntegerField(null=True, blank=True)
    duration = models.CharField(
            max_length=20,
            choices=DURATION_CHOICE,
            default='day',
            verbose_name='Duration'
        )
    duration_day = models.IntegerField(verbose_name='Duration Days', null=True, blank=True)
    duration_night = models.IntegerField(verbose_name='Duration Nights', null=True, blank=True)
    duration_hour = models.IntegerField(verbose_name='Duration Hours', null=True, blank=True)
    pickup_point = models.CharField(max_length=255, blank=True, null=True,
                                    verbose_name='Pickup Point')
    pickup_time = models.DateTimeField(verbose_name='Pickup Time', blank=True, null=True)
    drop_point = models.CharField(max_length=255, blank=True, null=True,
                                  verbose_name='Drop Point')
    drop_time = models.DateTimeField(verbose_name='Drop Time', blank=True, null=True)

    stage = models.CharField(
        max_length=20,
        choices=STAGES_CHOICES,
        default='pending',
        verbose_name='Stage'
    )

    is_submitted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'

    def __str__(self):
        return self.package_uid if self.package_uid else self.title


class PackageImage(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='packageimage_package')
    image = models.ImageField(upload_to='package_images/', null=True, default=None, blank=True)

    def __str__(self):
        return f"Image for {self.package.title}"


class Inclusions(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, blank=True, null=True, related_name='inclusion_package')
    activity = models.ForeignKey(
        Package, on_delete=models.CASCADE, blank=True, null=True, related_name='inclusion_activity')
    is_deleted = models.BooleanField(default=0)

    class Meta:
        verbose_name = 'Inclusions'
        verbose_name_plural = 'Inclusions'

    def __str__(self):
        return self.name

    def clean(self):
        # Check for uniqueness of country name (case-insensitive)
        inclusion = Inclusions.objects.filter(name__iexact=self.name).exclude(pk=self.pk)
        if inclusion.exists():
            raise ValidationError({'name': f'{self.name} already exists.'})

        # Check if the name contains only alphabetic characters
        if not self.name.replace(' ', '').isalpha():
            raise ValidationError(
                {'name': _('Inclusions name should contain only alphabetic characters.')})


class Exclusions(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, blank=True, null=True, related_name='exclusion_package')
    activity = models.ForeignKey(
        Package, on_delete=models.CASCADE, blank=True, null=True, related_name='exclusion_activity')

    class Meta:
        verbose_name = 'Exclusions'
        verbose_name_plural = 'Exclusions'

    def __str__(self):
        return self.name

    def clean(self):
        # Check for uniqueness of country name (case-insensitive)
        exclusion = Exclusions.objects.filter(name__iexact=self.name).exclude(pk=self.pk)
        if exclusion.exists():
            raise ValidationError({'name': f'{self.name} already exists.'})

        # Check if the name contains only alphabetic characters
        if not self.name.replace(' ', '').isalpha():
            raise ValidationError({'name': _('Exclusions name should contain only alphabetic characters.')})


class ItineraryDay(BaseModel):
    # package = models.ForeignKey(
    #     Package, on_delete=models.CASCADE, related_name='itinerardays')
    day = models.CharField(max_length=255, default="")
    place = models.CharField(max_length=255, default="", blank=True, null=True)
    description = models.TextField(default="", blank=True, null=True)

    class Meta:
        verbose_name = 'Itinerary Day'
        verbose_name_plural = 'Itinerary Day'

    def __str__(self):
        return f"{self.day} - {self.place} - {self.description}"

class Itinerary(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='itinerary_package')
    overview = models.TextField(blank=True, default="")
    itinerary_day = models.ManyToManyField(
        ItineraryDay, related_name='itinerary_itinerary_day')
    inclusions = models.ManyToManyField(Inclusions, related_name='itinerary_inclusions', blank=True)
    exclusions = models.ManyToManyField(Exclusions, related_name='itinerary_exclusions', blank=True)

    class Meta:
        verbose_name = 'Itinerary'
        verbose_name_plural = 'Itinerary'


class InclusionInformation(BaseModel):
    inclusion = models.ForeignKey(
        Inclusions, on_delete=models.CASCADE, 
        related_name='inclusioninformation_inclusion', null=True, blank=True)
    details = models.TextField(blank=True, null=True, default="")

    class Meta:
        verbose_name = 'Inclusion Information'
        verbose_name_plural = 'Inclusion Information'


class ExclusionInformation(BaseModel):
    exclusion = models.ForeignKey(
        Exclusions, on_delete=models.CASCADE, 
        related_name='exclusioninformation_exclusion', null=True, blank=True)
    details = models.TextField(blank=True, null=True, default="")

    class Meta:
        verbose_name = 'Exclusion Information'
        verbose_name_plural = 'Exclusion Information'


class PackageInformations(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='packageinformations_package')
    # inclusiondetails = models.ForeignKey(
    #     InclusionInformation, on_delete=models.CASCADE,
    #     related_name='informations_inclusion', null=True, blank=True)
    inclusiondetails = models.ManyToManyField(
        InclusionInformation, related_name='packageinformations_inclusiondetails', blank=True)
    exclusiondetails = models.ManyToManyField(
        ExclusionInformation, related_name='packageinformations_exclusiondetails', blank=True)
    # exclusiondetails = models.ForeignKey(
    #     ExclusionInformation, on_delete=models.CASCADE,
    #     related_name='informations_exclusion', null=True, blank=True)
    important_message = models.TextField(blank=True, default="",
                                         verbose_name="important Message")
    
    class Meta:
        verbose_name = 'Information'
        verbose_name_plural = 'Informations'


class Currency(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currency'

    def __str__(self):
        return self.name


class Pricing(BaseModel):
    PRICING_GROUP_CHOICE = [
        ('per_person', 'Per Person'),
        ('per_group', 'Per Group'),
    ]

    #field for group pricing
    group_rate = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    group_commission = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    group_agent_amount = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)

    #field for per-person pricing
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='pricing_package')
    pricing_group = models.CharField(
        max_length=25, choices=PRICING_GROUP_CHOICE, default='per_person')
    price = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='pricing_price',
        null=True, blank=True)
    adults_rate = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    adults_commission = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    adults_agent_amount = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    child_rate = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    child_commission = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    child_agent_amount = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    infant_rate = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    infant_commission = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    infant_agent_amount = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Pricing'
        verbose_name_plural = 'Pricing'


class TourCategory(BaseModel):
    CATEGORY_TYPE_CHOICE = [
        ("through_out_year", "Through Out Year"),
        ("seasonal", "Seasonal"),
        ("fixed_departure", "Fixed Departure")
    ]

    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='tourcategory_package')
    type = models.CharField(
        max_length=255, choices=CATEGORY_TYPE_CHOICE, default='through_out_year')
    start_at = models.DateField(null=True, blank=True)
    end_at = models.DateField(null=True, blank=True)
    selected_week_days = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Tour Category'
        verbose_name_plural = 'Tour Categories'

    def is_through_out_year(self):
        return self.category_type == 'through_out_year'

    def is_seasonal(self):
        return self.category_type == 'seasonal'

    def is_fixed_departure(self):
        return self.category_type == 'fixed_departure'
    

class PackageCancellationCategory(BaseModel):
    from_day = models.IntegerField(null=True, blank=True)
    to_day = models.IntegerField(null=True, blank=True)
    amount_percent = models.CharField(max_length=255)


class CancellationPolicy(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='cancellationpolicy_package')
    category = models.ManyToManyField(PackageCancellationCategory,
                                      related_name='cancellationpolicy_category',
                                      blank=True)

    class Meta:
        verbose_name = 'Cancellation Policy'
        verbose_name_plural = 'Cancellation Policies'


class PackageFaqCategory(BaseModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    class Meta:
        verbose_name = 'FAQAnswer'
        verbose_name_plural = 'FAQAnswers'


class PackageFaqQuestionAnswer(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='packagefaq_package')
    category = models.ManyToManyField(PackageFaqCategory,
                                      related_name='package_faq_category',
                                      blank=True)


class Booking(BaseModel):

    BOOKING_STATUS =(
            ("ORDERED", "ORDERED"),
            ("SUCCESSFUL", "SUCCESSFUL"),
            ("CANCELLED", "CANCELLED"),
            ("REFUNDED REQUESTED", "REFUNDED REQUESTED"),
            ("REFUNDED", "REFUNDED"),
            ("FAILED","FAILED")
          
            )
    
    booking_id = models.CharField(max_length=256, null=True, blank=True, verbose_name='Booking UID')
    object_id = models.UUIDField(
        unique=True,null=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, null=True, blank=True,related_name='package_booking')
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, null=True, blank=True,related_name='activity_booking')
    adult = models.IntegerField(null=True, blank=True)
    child = models.IntegerField(null=True, blank=True)
    infant = models.IntegerField(null=True, blank=True)
    booking_amount = models.DecimalField(default=0,  max_digits=10, decimal_places=2,null=True, blank=True)
    order_id = models.CharField(max_length=100,null=True, blank=True)
    payment_id = models.CharField(max_length=100,null=True, blank=True)
    tour_date = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    booking_status  =  models.CharField(choices = BOOKING_STATUS,
                                        max_length=50, verbose_name='Booking Status',
                                        blank=True,null=True)
    refund_amount = models.DecimalField(default=0,  max_digits=10, decimal_places=2,null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookings_user',null=True, blank=True)
    cancellation_description = models.TextField(blank=True, null=True)
    booking_type  =  models.CharField(choices = BOOKING_TYPE,max_length=50,blank=True,null=True)


    def __str__(self):
        return self.booking_id

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'


class Transaction(BaseModel):

    REFUND_STATUS =(
            ("PENDING", "PENDING"),
            ("CANCELLED", "CANCELLED"),
            ("REFUNDED", "REFUNDED"),
          
            )
    
    transaction_uid = models.CharField(max_length=256, null=True, blank=True, verbose_name='Transaction UID')
    object_id = models.UUIDField(
        unique=True,null=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='transaction_package')
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='transaction_booking')
    refund_status  =  models.CharField(choices = REFUND_STATUS,max_length=50,blank=True,null=True)
    refund_amount = models.DecimalField(default=0,  max_digits=10, decimal_places=2,null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_transaction',null=True, blank=True)

    

    def __str__(self):
        return self.transaction_uid

    class Meta:
        verbose_name = 'Transactions'
        verbose_name_plural = 'Transactions'


class UserRefundTransaction(AuditFields):

    REFUND_STATUS =(
            ("PENDING", "PENDING"),
            ("CANCELLED", "CANCELLED"),
            ("REFUNDED", "REFUNDED"),
          
            )
    
    refund_uid = models.CharField(max_length=256, null=True, blank=True, verbose_name='Refund UID')
    object_id = models.UUIDField(
        unique=True,null=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='user_refund_transaction_package')
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, null=True, blank=True,related_name='user_refund_transaction_activity')
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='user_refund_transaction_booking')
    refund_status  =  models.CharField(choices = REFUND_STATUS, max_length=50,
                                       blank=True, null=True, verbose_name='Refund Status')
    refund_amount = models.DecimalField(default=0,  max_digits=10, decimal_places=2,null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transaction_refund_user',null=True, blank=True)
    refund_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.refund_uid

    class Meta:
        verbose_name = 'User Transaction'
        verbose_name_plural = 'User Transaction'


class AgentTransactionSettlement(AuditFields):

    PAYMENT_SETTLEMENT_STATUS =(
            ("PENDING", "PENDING"),
            ("SUCCESSFUL", "SUCCESSFUL"),
            ("FAILED","FAILED")
            )
    
    transaction_id = models.CharField(max_length=256, null=True, blank=True, verbose_name='Transaction UID')
    object_id = models.UUIDField(
        unique=True,null=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='agent_transaction_settlement_package')
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, null=True, blank=True,related_name='agent_transaction_settlement_activity')
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='agent_transaction_settlement_booking')
    payment_settlement_status  =  models.CharField(default="PENDING",choices = PAYMENT_SETTLEMENT_STATUS,
                                                   max_length=50,blank=True,null=True, verbose_name='Payment Settlement Status')
    payment_settlement_amount = models.DecimalField(default=0,  max_digits=10, decimal_places=2,null=True, blank=True)
    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name='transaction_settlement_agent',null=True, blank=True)
    payment_settlement_date = models.DateField(null=True, blank=True)
    booking_type  =  models.CharField(choices = BOOKING_TYPE, max_length=50,
                                      blank=True,null=True, verbose_name='Booking Type')


    def __str__(self):
        return self.transaction_id if self.transaction_id else self.booking.booking_id

    class Meta:
        verbose_name = 'Agent Transaction'
        verbose_name_plural = 'Agent Transaction'


# class TourType(AuditFields):
#     title = models.CharField(max_length=256, null=True, blank=True)

#     class Meta:
#         verbose_name = "Tour Type"
#         verbose_name_plural = "Tour Type"

#     def __str__(self):
#         return self.title
    
class AdvanceAmountPercentageSetting(AuditFields):
    percentage = models.DecimalField(default=0,  max_digits=10, decimal_places=2,null=True, blank=True)
    
    class Meta:
        verbose_name = "Advance Amount Percentage"
        verbose_name_plural = "Advance Amount Percentage"




class Attraction(BaseModel):
    title = models.CharField(max_length=255, unique=True)
    overview = models.TextField(blank=True, default="")
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='attaction_state',
        null=True, blank=True)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='attraction_state',
        null=True, blank=True)
    thumb_img = models.ImageField(
        upload_to='attraction/thumb_images/', 
        null=True, default=None, blank=True, verbose_name="Thumb Image")
    cover_img = models.ImageField(
        upload_to='attraction/cover_image/', 
        null=True, default=None, blank=True, verbose_name="Cover Image")

    class Meta:
        verbose_name = 'Attraction'
        verbose_name_plural = 'Attractions'

    def __str__(self):
        return self.title

    # def clean(self):
    #     # Check if the title contains only alphabetic characters
    #     if not self.title.replace(' ', '').isalpha():
    #         raise ValidationError({'title': _('Title should contain only alphabetic characters.')})


class AttractionImage(models.Model):
    attraction = models.ForeignKey(
        Attraction, on_delete=models.CASCADE, related_name='attracionimages')
    image = models.ImageField(upload_to='attraction_images/', null=True, default=None, blank=True)

    def __str__(self):
        return f"Image for {self.attraction.title}"


class UserReview(BaseModel):
    object_id = models.UUIDField(
        unique=True,null=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, null=True, blank=True,related_name='package_review')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,null=True, blank=True,
        related_name='user_review', verbose_name='User')
    rating = models.IntegerField(verbose_name='Rating')
    review = models.TextField(blank=True,null=True )
    is_active = models.BooleanField(default=1)
    is_deleted = models.BooleanField(default=0)
    homepage_display = models.BooleanField(default=0)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE,null=True, blank=True, related_name='user_review_booking')
    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE,null=True, blank=True, related_name='user_review_agent')
    agent_comment = models.TextField(blank=True,null=True )
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, null=True, blank=True,related_name='activity_review')

    class Meta:
        verbose_name = 'User Review'
        verbose_name_plural = 'User Reviews'


class ContactPerson(AuditFields):
    object_id = models.UUIDField(
        unique=True,null=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE,null=True, blank=True, related_name='contact_person_booking')
    full_name = models.CharField(max_length=256, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)



"""
ACTIVITY MODELS
"""


class ActivityImage(BaseModel):
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='activityimages_activity')
    image = models.ImageField(upload_to='activity_images/', null=True, default=None, blank=True)

    def __str__(self):
        return f"Image for {self.activity.title}"


class ActivityInclusions(BaseModel):
    # STAGES_CHOICES = [
    #     ('pending', _('Pending')),
    #     ('approved', _('Approved')),
    #     ('rejected', _('Rejected')),
    # ]

    name = models.CharField(max_length=255, unique=True)
    # stage = models.CharField(
    #     max_length=20,
    #     choices=STAGES_CHOICES,
    #     default='pending',
    #     verbose_name='Stage'
    # )
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, blank=True, null=True, related_name='inclusion_activity')

    class Meta:
        verbose_name = 'Activity Inclusions'
        verbose_name_plural = 'Activity Inclusions'

    def __str__(self):
        return self.name

    def clean(self):
        # Check for uniqueness of country name (case-insensitive)
        inclusion = ActivityInclusions.objects.filter(name__iexact=self.name).exclude(pk=self.pk)
        if inclusion.exists():
            raise ValidationError({'name': f'{self.name} already exists.'})

        # Check if the name contains only alphabetic characters
        if not self.name.replace(' ', '').isalpha():
            raise ValidationError(
                {'name': _('Inclusions name should contain only alphabetic characters.')})


class ActivityExclusions(BaseModel):
    # STAGES_CHOICES = [
    #     ('pending', _('Pending')),
    #     ('approved', _('Approved')),
    #     ('rejected', _('Rejected')),
    # ]
    name = models.CharField(max_length=255, unique=True)
    # stage = models.CharField(
    #     max_length=20,
    #     choices=STAGES_CHOICES,
    #     default='pending',
    #     verbose_name='Stage'
    # )
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, blank=True, null=True, related_name='exclusion_activity')
    

    class Meta:
        verbose_name = 'Activity Exclusions'
        verbose_name_plural = 'Activity Exclusions'

    def __str__(self):
        return self.name

    def clean(self):
        # Check for uniqueness of country name (case-insensitive)
        exclusion = ActivityExclusions.objects.filter(name__iexact=self.name).exclude(pk=self.pk)
        if exclusion.exists():
            raise ValidationError({'name': f'{self.name} already exists.'})

        # Check if the name contains only alphabetic characters
        if not self.name.replace(' ', '').isalpha():
            raise ValidationError({'name': _('Exclusions name should contain only alphabetic characters.')})


class ActivityItineraryDay(BaseModel):
    day = models.CharField(max_length=255, default="")
    place = models.CharField(max_length=255, default="", blank=True, null=True)
    description = models.TextField(default="", blank=True, null=True)

    class Meta:
        verbose_name = 'Itinerary Day'
        verbose_name_plural = 'Itinerary Day'


class ActivityItinerary(BaseModel):
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='activity_itinerary_activity')
    overview = models.TextField(blank=True, default="")
    itinerary_day = models.ManyToManyField(
        ActivityItineraryDay, related_name='activity_itinerary_itinerary_day')
    inclusions = models.ManyToManyField(Inclusions, related_name='activity_itinerary_inclusions', blank=True)
    exclusions = models.ManyToManyField(Exclusions, related_name='activity_itinerary_exclusions', blank=True)

    class Meta:
        verbose_name = 'Activity Itinerary'
        verbose_name_plural = 'Activity Itinerary'


class ActivityInclusionInformation(BaseModel):
    inclusion = models.ForeignKey(
        Inclusions, on_delete=models.CASCADE, 
        related_name='activity_inclusioninformation_inclusion', null=True, blank=True)
    details = models.TextField(blank=True, null=True, default="")

    class Meta:
        verbose_name = 'Activity Inclusion Information'
        verbose_name_plural = 'Activity Inclusion Information'


class ActivityExclusionInformation(BaseModel):
    exclusion = models.ForeignKey(
        Exclusions, on_delete=models.CASCADE, 
        related_name='activity_exclusioninformation_exclusion', null=True, blank=True)
    details = models.TextField(blank=True, null=True, default="")

    class Meta:
        verbose_name = 'Activity Exclusion Information'
        verbose_name_plural = 'Activity Exclusion Information'


class ActivityInformations(BaseModel):
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='activity_informations_activity')
    inclusiondetails = models.ManyToManyField(
        ActivityInclusionInformation, related_name='activity_informations_inclusiondetails', blank=True)
    exclusiondetails = models.ManyToManyField(
        ActivityExclusionInformation, related_name='pactivity_informations_exclusiondetails', blank=True)
    important_message = models.TextField(blank=True, default="",
                                         verbose_name="important Message")
    
    class Meta:
        verbose_name = 'Activity Information'
        verbose_name_plural = 'Activity Informations'


class ActivityPricing(BaseModel):
    PRICING_GROUP_CHOICE = [
        ('per_person', 'Per Person'),
        ('per_group', 'Per Group'),
    ]

    #field for group pricing
    group_rate = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    group_commission = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    group_agent_amount = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)

    #field for per-person pricing
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='activity_pricing_activity')
    pricing_group = models.CharField(
        max_length=25, choices=PRICING_GROUP_CHOICE, default='per_person')
    price = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='activity_pricing_price',
        null=True, blank=True)
    adults_rate = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    adults_commission = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    adults_agent_amount = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    child_rate = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    child_commission = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    child_agent_amount = models.DecimalField(
        default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    infant_rate = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    infant_commission = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)
    infant_agent_amount = models.DecimalField(
        default=0,  max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Activity Pricing'
        verbose_name_plural = 'Activity Pricing'


class ActivityTourCategory(BaseModel):
    CATEGORY_TYPE_CHOICE = [
        ("through_out_year", "Through Out Year"),
        ("seasonal", "Seasonal"),
        ("fixed_departure", "Fixed Departure")
    ]

    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='activity_tourcategory_activity')
    type = models.CharField(
        max_length=255, choices=CATEGORY_TYPE_CHOICE, default='through_out_year')
    start_at = models.DateField(null=True, blank=True)
    end_at = models.DateField(null=True, blank=True)
    selected_week_days = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Activity Tour Category'
        verbose_name_plural = 'Activity Tour Categories'

    def is_through_out_year(self):
        return self.category_type == 'through_out_year'

    def is_seasonal(self):
        return self.category_type == 'seasonal'

    def is_fixed_departure(self):
        return self.category_type == 'fixed_departure'
    

class ActivityCancellationCategory(BaseModel):
    from_day = models.IntegerField(null=True, blank=True)
    to_day = models.IntegerField(null=True, blank=True)
    amount_percent = models.CharField(max_length=255)


class ActivityCancellationPolicy(BaseModel):
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='cancellationpolicy_activity')
    category = models.ManyToManyField(ActivityCancellationCategory,
                                      related_name='activity_cancellationpolicy_category',
                                      blank=True)

    class Meta:
        verbose_name = 'Activity Cancellation Policy'
        verbose_name_plural = 'Activity Cancellation Policies'


class ActivityFaqCategory(BaseModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    class Meta:
        verbose_name = 'Activity FAQAnswer'
        verbose_name_plural = 'Activity FAQAnswers'


class ActivityFaqQuestionAnswer(BaseModel):
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name='activityfaq_activity')
    category = models.ManyToManyField(ActivityFaqCategory,
                                      related_name='activity_faq_category',
                                      blank=True)
