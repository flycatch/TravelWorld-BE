from api.models import *
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver


@receiver(post_save, sender=Agent)
def send_email_on_stage_update(sender, instance, created, **kwargs):
    if not created:
        subject = ''
        message = ''
        if instance.stage == 'approved':
            print(instance.stage)
            subject = 'Welcome To TravelWorld'
            message = f'Hi {instance.username}, Your application to TravelWorld is approved. You can login using our portal. Thank You'
        elif instance.stage == 'rejected':
            subject = 'Application Rejected by TravelWorld'
            message = f'Hi {instance.username}, Your application to TravelWorld is rejected. Please contact customer portal. Thank You'

        if subject and message:
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [instance.email]

            send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Package)
def send_email_on_stage_update_package(sender, instance, created, **kwargs):
    if not created:
        subject = ''
        message = ''
        if instance.stage == 'approved':
            print(instance.stage)
            subject = 'Explore World - Package Approved'
            message = f'Hi {instance.agent.username}, Your Package "{instance.package_uid} - {instance.title}" is approved by admin. Thank You'
        elif instance.stage == 'rejected':
            subject = 'Explore World - Package Rejected'
            message = f'Hi {instance.agent.username}, Your Package "{instance.package_uid} - {instance.title}" is Rejected by admin. Please contact customer portal. Thank You'

        if subject and message:
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [instance.agent.email]

            send_mail(subject, message, from_email, recipient_list)


@receiver(post_save, sender=Activity)
def send_email_on_stage_update_activity(sender, instance, created, **kwargs):
    if not created:
        subject = ''
        message = ''
        if instance.stage == 'approved':
            print(instance.stage)
            subject = 'Explore World - Activity Approved'
            message = f'Hi {instance.agent.username}, Your Activity "{instance.activity_uid} - {instance.title}" is approved by admin. Thank You'
        elif instance.stage == 'rejected':
            subject = 'Explore World - Activity Rejected'
            message = f'Hi {instance.agent.username}, Your Activity "{instance.activity_uid} - {instance.title}" is Rejected by admin. Please contact customer portal. Thank You'

        if subject and message:
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [instance.agent.email]

            send_mail(subject, message, from_email, recipient_list)


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


@receiver(post_save, sender=Pricing)
def customer_unique_id(sender, instance, created, **kwargs):
    print('Signal triggered:', instance.id, created)

    if not created:
        print("hi")
        # Try to get the new record
        new_record = instance.history.first()

        if new_record:

            # Try to get the previous record
            old_record = new_record.prev_record

            # Check if there is a previous record
            if old_record:
                record_diff = new_record.diff_against(old_record)
                print(record_diff)
                changed_fields = record_diff.changed_fields

                new_record.changed_fields = {'changed_fields': changed_fields}

                print(new_record)
                new_record.save()

            else:
                print('No previous record. This is the first version.')
        else:
            print('No historical record found.')



@receiver(post_save, sender=Pricing)
def update_package_min_price_on_save(sender, instance, **kwargs):
    if instance.package:
        instance.package.update_min_price()

@receiver(post_delete, sender=Pricing)
def update_package_min_price_on_delete(sender, instance, **kwargs):
    if instance.package:
        instance.package.update_min_price()