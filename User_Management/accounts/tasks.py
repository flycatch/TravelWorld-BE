from celery import shared_task
from django.core.mail import send_mail
from User_Management.settings import *
from django.template.loader import render_to_string
from accounts.models import *

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


@shared_task
def send_booking_email(subject, template_name, recipient_email, context):
    print("Inside Celery task for sending email")

    instance = Booking.objects.get(object_id=context['booking_object_id'])

    if context['deal_type']=='PACKAGE':
        # Get all locations
        locations = instance.package.locations.all()
        
        # Prepare location details
        location_list = []
        for location in locations:
            state_name = location.state.name if location.state else 'Unknown State'
            country_name = location.country.name if location.country else 'Unknown Country'
            destination_names = ', '.join(str(dest) for dest in location.destinations.all())
            location_list.append({
                'state': state_name,
                'country': country_name,
                'destinations': destination_names
            })
        
        context.update({
            'title': instance.package.title,
            'locations':location_list,
            'tour_class': instance.package.tour_class,
           
        })
    else:
        # Get all locations
        locations = instance.activity.locations.all()
        
        # Prepare location details
        location_list = []
        for location in locations:
            state_name = location.state.name if location.state else 'Unknown State'
            country_name = location.country.name if location.country else 'Unknown Country'
            destination_names = ', '.join(str(dest) for dest in location.destinations.all())
            location_list.append({
                'state': state_name,
                'country': country_name,
                'destinations': destination_names
            })

        context.update({
            'title': instance.activity.title,
            'locations':location_list,
            'tour_class': instance.activity.tour_class,  
        })

    context.update({
            'booking_id':instance.booking_id,
            'tour_date': instance.tour_date,
            'adult':instance.adult,
            'child': instance.child,
            'infant':instance.infant,
            'booking_date':instance.created_on,
            'booking_amount':instance.booking_amount,
            'object_id':instance.object_id,
        })

    html_content = render_to_string(template_name, context)
    send_mail(
        subject,
        '',
        EMAIL_HOST_USER,
        [recipient_email],
        html_message=html_content,
        fail_silently=False
    )
