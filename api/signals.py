from api.models import Agent, Booking,Transaction, Activity, Package, User
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
        booking_id = f"EWBK-{instance.id}"
        instance.booking_id = booking_id
        instance.save()

@receiver(post_save, sender=Transaction)
def refund_code_created(sender, instance, created, **kwargs):
    
    if created:
        refund_id = f"EWRF-{instance.id}"
        instance.refund_id = refund_id
        instance.save()

@receiver(post_save, sender=Package)
def package_code_created(sender, instance, created, **kwargs):
    
    if created:
        package_uid = f"EWPKG-{instance.id}"
        instance.package_uid = package_uid
        instance.save()

@receiver(post_save, sender=Activity)
def activity_code_created(sender, instance, created, **kwargs):
    
    if created:
        activity_uid = f"EWACT-{instance.id}"
        instance.activity_uid = activity_uid
        instance.save()

@receiver(post_save, sender=User)
def user_code_created(sender, instance, created, **kwargs):
    
    if created:
        user_uid = f"EWUSR-{instance.id}"
        instance.user_uid = user_uid
        instance.save()