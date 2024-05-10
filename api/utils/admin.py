from django.utils.html import format_html


def stage_colour(stage):
    if stage == 'approved':
        color = '#62cd61'
        bg_color = '#ebf9eb'
    elif stage == 'rejected':
        color = '#f46566'
        bg_color = '#fdebeb'
    else:
        color = '#4576dd'  # Default color
        bg_color = '#cee8ff'

    return format_html(
        '<span style="color: {};  border: 1px solid; background-color: {}; \
            padding-left: 8px; padding-right: 8px; border-radius: 4px; text-transform: \
                uppercase; min-width: 100px; display: inline-block; text-align: center;">{}</span>',
                color, bg_color, stage)

def account_verification_status_colour(status):
    # Define colors based on the verification status
    if status == 'approved':
        color = '#62cd61'  # Green color for approved status
        bg_color = '#ebf9eb'  # Light green background
    elif status == 'rejected':
        color = '#f46566'  # Red color for rejected status
        bg_color = '#fdebeb'  # Light red background
    elif status == 'pending':
        color = '#e6b51e'  # Yellow color for pending status
        bg_color = '#fef8e8'  # Light yellow background
    else:
        color = 'black'  # Default color for unknown status
        bg_color = ''  # No background color for unknown status
    
    # Construct HTML span element with inline styles based on the status and colors
    return format_html(
        '<span style="color: {};  border: 1px solid; background-color: {}; \
            padding-left: 8px; padding-right: 8px; border-radius: 4px; text-transform: \
                uppercase; min-width: 100px; display: inline-block; text-align: center;">{}</span>',
        color, bg_color, status)

def status_colour(status):
    if status == 'active':
        color = '#62cd61'
        bg_color = '#ebf9eb'
    else:
        color = '#9a9da0'  # Default color
        bg_color = '#e0e2e4'  # Background color for 'rejected'

    return format_html(
        '<span style="color: {};  border: 1px solid; background-color: {}; \
            padding-left: 8px; padding-right: 8px; border-radius: 4px; text-transform: \
                uppercase; min-width: 85px; display: inline-block; text-align: center;">{}</span>',
                color, bg_color, status)

def booking_status_colour(booking_status):
    if booking_status == 'SUCCESSFUL':
        color = '#62cd61'
        bg_color = '#ebf9eb'
    elif booking_status == 'ORDERED':
        color = '#4576dd'
        bg_color = '#cee8ff'
    elif booking_status == 'PENDING':
        color = '#e6b51e'
        bg_color = '#fef8e8'
    elif booking_status == 'CANCELLED':
        color = 'gray'
        bg_color = ''
    elif booking_status == 'REFUNDED REQUESTED':
        color = '#b8530b'
        bg_color = '#fef8e8'
    elif booking_status == 'REFUNDED':
        color = '#62cd61'
        bg_color = '#ebf9eb'
    elif booking_status == 'FAILED':
        color = '#f46566'
        bg_color = '#fdebeb'
    else:
        color = 'black'  # Default color
        bg_color = ''

    return format_html(
        '<span style="color: {};  border: 1px solid; background-color: {}; \
            padding-left: 8px; padding-right: 8px; border-radius: 4px; text-transform: \
                uppercase; min-width: 185px; display: inline-block; text-align: center;">{}</span>',
                color, bg_color, booking_status)

def refund_status_colour(refund_status):
    if refund_status == 'PENDING':
        color = '#e6b51e'
        bg_color = '#fef8e8'
    elif refund_status == 'CANCELLED':
        color = '#f46566'
        bg_color = '#fdebeb'
    elif refund_status == 'FAILED':
        color = '#f46566'
        bg_color = '#fdebeb'
    elif refund_status == 'SUCCESSFUL':
        color = '#62cd61'  # Default color
        bg_color = '#ebf9eb'
    elif refund_status == 'REFUNDED':
        color = '#62cd61'
        bg_color = '#ebf9eb'
    else:
        color = '#f46566'
        bg_color = '#fdebeb'

    return format_html(
        '<span style="color: {};  border: 1px solid; background-color: {}; \
            padding-left: 8px; padding-right: 8px; border-radius: 4px; text-transform: \
                uppercase; min-width: 100px; display: inline-block; text-align: center;">{}</span>',
                color, bg_color, refund_status)