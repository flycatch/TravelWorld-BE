"""
Module for defining custom filter sets for Booking and AgentTransactionSettlement models.

This module includes:
- BookingFilter: A filter set for filtering bookings based on various criteria.
- AgentTransactionSettlementFilter: A filter set for filtering agent transaction settlements
    based on their payment settlement status.

Classes:
    - BookingFilter: Filter set for Booking model.
    - AgentTransactionSettlementFilter: Filter set for AgentTransactionSettlement model.
"""
from django_filters import rest_framework as django_filters
from api.models import (Booking, AgentTransactionSettlement)


class BookingFilter(django_filters.FilterSet):
    """
    Filter for various fields in the Booking model.

    This filter set allows you to filter bookings based on different criteria,
    including booking status, booking type, and tour date.

    Fields:
        booking_status (CharFilter): Filters bookings by their booking status.
        booking_type (CharFilter): Filters bookings by their booking type.
    """
    booking_status = django_filters.CharFilter(field_name='booking_status', lookup_expr='exact')
    booking_type = django_filters.CharFilter(field_name='booking_type', lookup_expr='exact')

    class Meta:
        """
        Meta options for BookingFilter.

        Attributes:
            model (api.models.Booking): The model that this filter set is based on.
            fields (list): The list of fields that this filter set can filter on.
        """
        model = Booking
        fields = ['booking_status', 'tour_date', 'booking_type']


class AgentTransactionSettlementFilter(django_filters.FilterSet):
    """
    Filter for various fields in the AgentTransactionSettlement model.

    This filter set allows you to filter agent transaction settlements based on 
    their payment settlement status.

    Fields:
        payment_settlement_status (CharFilter): Filters agent transaction settlements
        by their payment settlement status.
    """
    payment_settlement_status = django_filters.CharFilter(field_name='payment_settlement_status',
                                                          lookup_expr='exact')

    class Meta:
        """
        Meta options for AgentTransactionSettlementFilter.

        Attributes:
            model (api.models.AgentTransactionSettlement): The model that this
                filter set is based on.
            fields (list): The list of fields that this filter set can filter on.
        """
        model = AgentTransactionSettlement
        fields = ['payment_settlement_status']
