# update_baseuser_unique_username.py

from django.core.management.base import BaseCommand
from api.models import BaseUser,User


class Command(BaseCommand):
    help = 'Update unique_username field of BaseUser model'

    def handle(self, *args, **kwargs):
        users = BaseUser.objects.all()
        for user in users:
            # Update unique_username based on first_name, last_name, and id
            user.unique_username = f"{user.first_name.lower()}_{user.last_name.lower()}_{user.id}"
            user.save()

        c =User.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully updated unique_username for all BaseUser instances'))
