from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from api.common.models import BaseModel, BaseUser
# from api.common.library import encode


class User(BaseUser):
    profile_image = models.ImageField(upload_to='profile_images/user/', null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Agent(BaseUser):
    STAGES_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]


    profile_image = models.ImageField(upload_to='profile_images/agent/',null=True, blank=True)
    stage = models.CharField(
        max_length=20,
        choices=STAGES_CHOICES,
        default='pending',
        verbose_name=_('Stage'),
    )


    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return self.username
    

class Country(BaseModel):
    name = models.CharField(max_length=255)

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
        if not self.name.isalpha():
            raise ValidationError({'name': _('Country name should contain only alphabetic characters.')})

class State(BaseModel):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='states')

    class Meta:
        verbose_name = 'State'
        verbose_name_plural = 'States'

    def __str__(self):
        return self.name

    def clean(self):
        # Check for uniqueness of country name (case-insensitive)
        state = State.objects.filter(name__iexact=self.name, country=self.country).exclude(pk=self.pk)
        if state.exists():
            raise ValidationError({'name': f'{self.country} with {self.name} already exists.'})

        # Check if the name contains only alphabetic characters
        if not self.name.isalpha():
            raise ValidationError({'name': _('State name should contain only alphabetic characters.')})


class City(BaseModel):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='cities')

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
        if not self.name.isalpha():
            raise ValidationError({'name': _('City name should contain only alphabetic characters.')})


class TourType(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Tour Type'
        verbose_name_plural = 'Tour Type'

    def __str__(self):
        return self.name


class PackageCategory(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Package Category'
        verbose_name_plural = 'Package Category'

    def __str__(self):
        return self.name


class Package(BaseModel):
    STAGES_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name='packages')
    title = models.CharField(max_length=255)
    # images = models.CharField(
    #     max_length=255, blank=True, null=True)
    tour_type = models.ForeignKey(
        TourType, on_delete=models.CASCADE,
        related_name='packages',verbose_name='Tour Type')
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='packages')
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='packages')
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='packages')
    category = models.ForeignKey(
        PackageCategory, on_delete=models.CASCADE, related_name='packages')
    
    min_members = models.IntegerField()
    max_members = models.IntegerField()
    duration_day = models.IntegerField(verbose_name='Duration Day')
    duration_hour = models.IntegerField()
    pickup_point = models.CharField(max_length=255, blank=True, null=True, 
                                    verbose_name='Pickup Point')
    pickup_time = models.DateTimeField(verbose_name='Pickup Time')
    drop_point = models.CharField(max_length=255, blank=True, null=True,
                                  verbose_name='Drop Point')
    drop_time = models.DateTimeField(verbose_name='Drop Time')

    stage = models.CharField(
        max_length=20,
        choices=STAGES_CHOICES,
        default='pending',
        verbose_name='Stage'
    )

    class Meta:
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'

    def __str__(self):
        return self.title


class PackageImage(models.Model):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='packageimages')
    image = models.ImageField(upload_to='package_images/', null=True, default=None, blank=True)

    def __str__(self):
        return f"Image for {self.package.title}"
    

class ItineraryDay(BaseModel):
    day = models.CharField(max_length=255)
    plan = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = 'Itinerary Day'
        verbose_name_plural = 'Itinerary Day'


class Inclusions(BaseModel):
    STAGES_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    name = models.CharField(max_length=255, unique=True)
    stage = models.CharField(
        max_length=20,
        choices=STAGES_CHOICES,
        default='pending',
        verbose_name='Stage'
    )
    class Meta:
        verbose_name = 'Inclusions'
        verbose_name_plural = 'Inclusions'

    def __str__(self):
        return self.name

    def clean(self):
        # Check if the name contains only alphabetic characters
        if not self.name.isalpha():
            raise ValidationError({'name': _('Inclusions name should contain only alphabetic characters.')})


class Exclusions(BaseModel):
    STAGES_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]
    name = models.CharField(max_length=255, unique=True)
    stage = models.CharField(
        max_length=20,
        choices=STAGES_CHOICES,
        default='pending',
        verbose_name='Stage'
    )
    class Meta:
        verbose_name = 'Exclusions'
        verbose_name_plural = 'Exclusions'

    def __str__(self):
        return self.name

    def clean(self):
        # Check if the name contains only alphabetic characters
        if not self.name.isalpha():
            raise ValidationError({'name': _('Exclusions name should contain only alphabetic characters.')})


class Itinerary(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='itineraries')
    overview = models.TextField(blank=True, default="")
    itinerary_day = models.ManyToManyField(
        ItineraryDay, related_name='itineraries')
    inclusions = models.ManyToManyField(Inclusions, related_name='itineraries')
    exclusions = models.ManyToManyField(Exclusions, related_name='itineraries')

    class Meta:
        verbose_name = 'Itinerary'
        verbose_name_plural = 'Itinerary'


class HotelDetails(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    details = models.TextField(blank=True, default="")
    location_details = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = 'Hotel Details'
        verbose_name_plural = 'Hotel Details'

    def __str__(self):
        return self.name


class Guide(BaseModel):
    language = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Guide'
        verbose_name_plural = 'Guide'


class InformationActivities(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'Information Activities'
        verbose_name_plural = 'Information Activities'

    def __str__(self):
        return self.name


class ThingsToCarry(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Things To Carry'
        verbose_name_plural = 'Things To Carry'


class Informations(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='informations')
    hotel = models.ForeignKey(
        HotelDetails, on_delete=models.CASCADE, related_name='informations')
    meals = models.CharField(max_length=255, blank=True, null=True)
    transpotation = models.CharField(max_length=255, blank=True, null=True)
    entry_ticket = models.CharField(max_length=255, blank=True, null=True)
    train_ticket = models.CharField(max_length=255, blank=True, null=True)
    flight_ticket = models.CharField(max_length=255, blank=True, null=True)
    guide = models.ManyToManyField(Guide, related_name='informations')
    information_activities = models.ManyToManyField(
        InformationActivities, related_name='informations')
    things_to_carry = models.ManyToManyField(
        ThingsToCarry, related_name='informations')
    important_message = models.TextField(blank=True, default="")

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

    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='pricings')
    pricing_group = models.CharField(
        max_length=25, choices=PRICING_GROUP_CHOICE, default='per_person')
    price = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name='pricings')
    adults_rate = models.IntegerField()
    adults_commission = models.CharField(max_length=255, blank=True, null=True)
    adults_agent_amount = models.FloatField(default=0.0, blank=True, null=True)
    child_rate = models.IntegerField()
    child_commission = models.CharField(max_length=255, blank=True, null=True)
    child_agent_amount = models.FloatField(default=0.0, blank=True, null=True)
    infant_rate = models.IntegerField()
    infant_commission = models.CharField(max_length=255, blank=True, null=True)
    infant_agent_amount = models.FloatField(default=0.0, blank=True, null=True)
    group_rate = models.IntegerField()
    group_commission = models.CharField(max_length=255, blank=True, null=True)
    group_agent_amount = models.FloatField(default=0.0, blank=True, null=True)

    class Meta:
        verbose_name = 'Pricing'
        verbose_name_plural = 'Pricing'


class TourCategory(BaseModel):
    CATEGORY_TYPE_CHOICE = [
        ("through_out_year", "Through Out Year"),
        ("seasonal", "Seasonal"),
        ("fixed_departure", "Fixed_departure")
    ]

    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='tour_categories')
    type = models.CharField(
        max_length=255, choices=CATEGORY_TYPE_CHOICE, default='through_out_year')
    start_at = models.DateField()
    end_at = models.DateField()

    class Meta:
        verbose_name = 'Tour Category'
        verbose_name_plural = 'Tour Categories'


class CancellationPolicy(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='cancellation_policies')
    category = models.CharField(max_length=255)
    amount_percent = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Cancellation Policy'
        verbose_name_plural = 'Cancellation Policies'


class FAQQuestion(models.Model):
    question = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'FAQQuestion'
        verbose_name_plural = 'FAQQuestions'

    def __str__(self):
        return self.question


class FAQAnswer(models.Model):
    question = models.OneToOneField(FAQQuestion, on_delete=models.CASCADE, related_name='answer')
    answer = models.TextField()

    class Meta:
        verbose_name = 'FAQAnswer'
        verbose_name_plural = 'FAQAnswers'


class Booking(BaseModel):
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='bookings')
    adult = models.IntegerField()
    child = models.IntegerField()
    infant = models.IntegerField()
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'


class Activity(BaseModel):
    STAGES_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=255)
    stage = models.CharField(
        max_length=20,
        choices=STAGES_CHOICES,
        default='pending',
        verbose_name='Stage'
    )
    
    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

    def __str__(self):
        return self.name

    def clean(self):
        # Check if the name contains only alphabetic characters
        if not self.name.isalpha():
            raise ValidationError({'name': _('Activity name should contain only alphabetic characters.')})


class Attraction(BaseModel):
    title = models.CharField(max_length=255, unique=True)
    overview = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = 'Attraction'
        verbose_name_plural = 'Attractions'

    def __str__(self):
        return self.title

    def clean(self):
        # Check if the name contains only alphabetic characters
        if not self.title.isalpha():
            raise ValidationError({'name': _('Title should contain only alphabetic characters.')})


class AttractionImage(models.Model):
    attraction = models.ForeignKey(
        Attraction, on_delete=models.CASCADE, related_name='attracionimages')
    image = models.ImageField(upload_to='attraction_images/', null=True, default=None, blank=True)

    def __str__(self):
        return f"Image for {self.attraction.title}"
    

class UserReview(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='reviews')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    review = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = 'User Review'
        verbose_name_plural = 'User Reviews'
