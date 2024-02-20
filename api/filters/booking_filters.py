from api.models import (Booking, AgentTransactionSettlement)
from django_filters import rest_framework as django_filters



class BookingFilter(django_filters.FilterSet):
    booking_status = django_filters.CharFilter(field_name='booking_status', lookup_expr='exact')
    booking_type = django_filters.CharFilter(field_name='booking_type', lookup_expr='exact')


    class Meta:
        model = Booking
        fields = ['booking_status', 'tour_date','booking_type']


class AgentTransactionSettlementFilter(django_filters.FilterSet):
    payment_settlement_status = django_filters.CharFilter(field_name='payment_settlement_status', lookup_expr='exact')

    class Meta:
        model = AgentTransactionSettlement
        fields = ['payment_settlement_status']
