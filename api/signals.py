from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from api.models import Agent


@receiver(post_save, sender=Agent)
def send_email_on_status_update(sender, instance, created, **kwargs):
    if not created and instance.is_approved:  # Check if status was updated from False to True
        subject = 'Welcome To TravelWorld'
        message = f'Hi {instance.username}, Your application to TravelWorld is approved. You can login using our portal. Thank You'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]  # Add your email or recipient list here

        send_mail(subject, message, from_email, recipient_list)

@receiver(post_save, sender=Agent)
def send_email_on_status_update(sender, instance, created, **kwargs):
    if not created and instance.is_rejected:  # Check if status was updated from False to True
        subject = 'Application Rejected by TravelWorld'
        message = f'Hi {instance.username}, Your application to TravelWorld is rejected. Please contact customer section. Thank You'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]  # Add your email or recipient list here

        send_mail(subject, message, from_email, recipient_list)