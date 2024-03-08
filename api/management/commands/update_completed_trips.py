# update_baseuser_unique_username.py

from django.core.management.base import BaseCommand
from api.models import BaseUser,User,Booking
from datetime import datetime


class Command(BaseCommand):
    help = 'Update unique_username field of BaseUser model'

    def handle(self, *args, **kwargs):
        # Get today's date
        today = datetime.now().date()
        print(today)

        # Get bookings where the tour_date is in the past and is_trip_completed is False
        past_bookings = Booking.objects.filter(tour_date__lte=today, is_trip_completed=False)

        # Update is_trip_completed to True for these bookings
        for booking in past_bookings:
            print(booking)
            booking.is_trip_completed = True
            booking.save()

        # Optionally, you can print the number of bookings updated
        print(f"{past_bookings.count()} bookings updated.")
