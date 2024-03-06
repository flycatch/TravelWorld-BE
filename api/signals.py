from api.models import *
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver


# @receiver(post_save, sender=Agent)
# def send_email_on_stage_update(sender, instance, created, **kwargs):
#     if not created:
#         subject = ''
#         message = ''
#         if instance.stage == 'approved':
#             print(instance.stage)
#             subject = 'Welcome To TravelWorld'
#             message = f'Hi {instance.username}, Your application to TravelWorld is approved. You can log in using our portal. Thank You'
#         elif instance.stage == 'rejected':
#             subject = 'Application Rejected by TravelWorld'
#             message = f'Hi {instance.username}, Your application to TravelWorld is rejected. Please contact customer section. Thank You'

#         if subject and message:
#             from_email = settings.DEFAULT_FROM_EMAIL
#             recipient_list = [instance.email]

#             send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Booking)
def booking_code_created(sender, instance, created, **kwargs):
    
    if created:
        booking_id = f"EWBK-{instance.id}"
        instance.booking_id = booking_id
        instance.save()

# @receiver(post_save, sender=UserRefundTransaction)
# def refund_code_created(sender, instance, created, **kwargs):
    
#     if created:
#         refund_uid = f"EWRF-{instance.id}"
#         instance.refund_uid = refund_uid
#         instance.save()
        
from django.db.models.signals import pre_save

@receiver(pre_save, sender=UserRefundTransaction)
def generate_refund_uid(sender, instance, **kwargs):
    if instance.pk:  # Check if the instance already exists (not being created)
        try:
            # Get the original instance from the database
            original_instance = UserRefundTransaction.objects.get(pk=instance.pk)
            # Check if refund_status has changed to "REFUNDED"
            if original_instance.refund_status != 'REFUNDED' and instance.refund_status == 'REFUNDED':
                # Generate refund_uid
                refund_uid = f"EWRF-{instance.id}"
                instance.refund_uid = refund_uid
        except UserRefundTransaction.DoesNotExist:
            pass  # Handle if the original instance doesn't exist yet or has been deleted


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
        instance.unique_username = f'{instance.username}_{instance.id}'
        instance.save()


@receiver(post_save, sender=Agent)
def agent_code_created(sender, instance, created, **kwargs):
    
    if created:
        agent_uid = f"EWAG-{instance.id}"
        instance.agent_uid = agent_uid
        instance.unique_username = f'{instance.username}_{instance.id}'
        instance.save()