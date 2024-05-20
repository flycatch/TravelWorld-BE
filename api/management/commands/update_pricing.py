from django.core.management.base import BaseCommand
from api.models import Package

class Command(BaseCommand):
    help = 'Update the min_price field for existing Package records'

    def handle(self, *args, **kwargs):
        packages = Package.objects.all()
        for package in packages:
            package.update_min_price()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated min_price for package: {package.id}'))
