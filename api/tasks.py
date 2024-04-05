from celery import shared_task
from django.core.mail import send_mail
from TravelWorld.settings import *
from django.template.loader import render_to_string


@shared_task
def send_email(subject,message,email):
    print("inside celery")
    send_mail(
        subject,
        message ,
        EMAIL_HOST_USER,
        [email],
        fail_silently=False
    )

@shared_task
def send_enquiry_email(subject, template_name, recipient_email, context):
    print("Inside Celery task for sending email")
    html_content = render_to_string(template_name, context)
    send_mail(
        subject,
        '',
        EMAIL_HOST_USER,
        [recipient_email],
        html_message=html_content,
        fail_silently=False
    )
