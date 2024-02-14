from celery import shared_task
from django.core.mail import send_mail
from TravelWorld.settings import *


@shared_task
def send_email(subject,message,email):

    send_mail(
        subject,
        message ,
        EMAIL_HOST_USER,
        [email],
        fail_silently=False
    )

  

