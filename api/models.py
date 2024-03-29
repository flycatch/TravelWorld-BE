from django.db import models
from django.utils.translation import gettext_lazy as _

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
    profile_image = models.ImageField(upload_to='profile_images/agent/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'

    def __str__(self):
        return self.username
    

class Country(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class State(BaseModel):
    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='states')

    def __str__(self):
        return self.name


class City(BaseModel):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name


class TourType(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class PackageCategory(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Package(BaseModel):
    agent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='packages')
    title = models.CharField(max_length=255)
    images = models.CharField(
        max_length=255, blank=True, null=True)
    tour_type = models.ForeignKey(
        TourType, on_delete=models.CASCADE, related_name='packages')
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
    duration_day = models.IntegerField()
    duration_hour = models.IntegerField()
    pickup_point = models.CharField(max_length=255, blank=True, null=True)
    pickup_time = models.DateTimeField()
    drop_point = models.CharField(max_length=255, blank=True, null=True)
    drop_time = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ItineraryDay(BaseModel):
    day = models.CharField(max_length=255)
    plan = models.TextField(blank=True, default="")


class Inclusions(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Exclusions(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Itinerary(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='itineraries')
    overview = models.TextField(blank=True, default="")
    itinerary_day = models.ManyToManyField(
        ItineraryDay, related_name='itineraries')
    inclusions = models.ManyToManyField(Inclusions, related_name='itineraries')
    exclusions = models.ManyToManyField(Exclusions, related_name='itineraries')


class HotelDetails(BaseModel):
    name = models.CharField(max_length=255)
    details = models.TextField(blank=True, default="")
    location_details = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class Guide(BaseModel):
    language = models.CharField(max_length=255)


class InformationActivities(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ThingsToCarry(BaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


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


class Currency(BaseModel):
    name = models.CharField(max_length=255)

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


class CancellationPolicy(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='cancellation_policies')
    category = models.CharField(max_length=255)
    amount_percent = models.CharField(max_length=255)


# class Faq(BaseModel):
#     package = models.ForeignKey(
#         Package, on_delete=models.CASCADE, related_name='faqs')
#     question = models.CharField(max_length=255)
#     answer = models.TextField(blank=True, default="")

class FAQQuestion(models.Model):
    question = models.CharField(max_length=255)

    def __str__(self):
        return self.question


class FAQAnswer(models.Model):
    question = models.OneToOneField(FAQQuestion, on_delete=models.CASCADE, related_name='answer')
    answer = models.TextField()


class Booking(BaseModel):
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookings')
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='bookings')
    adult = models.IntegerField()
    child = models.IntegerField()
    infant = models.IntegerField()
    is_cancelled = models.BooleanField(default=False)


class Activity(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=255)
    is_published = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Attraction(BaseModel):
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='attractions')
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True, default="")
    image = models.ImageField(
        upload_to='attraction_images/', null=True, default=None, blank=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class UserReview(BaseModel):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name='reviews')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    review = models.TextField(blank=True, default="")
