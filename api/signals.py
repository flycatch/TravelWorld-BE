from api.models import Agent, Booking
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Agent)
def send_email_on_stage_update(sender, instance, created, **kwargs):
    if not created:
        subject = ''
        message = ''
        if instance.stage == 'approved':
            print(instance.stage)
            subject = 'Welcome To TravelWorld'
            message = f'Hi {instance.username}, Your application to TravelWorld is approved. You can log in using our portal. Thank You'
        elif instance.stage == 'rejected':
            subject = 'Application Rejected by TravelWorld'
            message = f'Hi {instance.username}, Your application to TravelWorld is rejected. Please contact customer section. Thank You'

        if subject and message:
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [instance.email]

            send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Booking)
def booking_code_created(sender, instance, created, **kwargs):
    
    if created:
        booking_id = f"BK-{instance.id}"
        instance.booking_id = booking_id
        instance.save()