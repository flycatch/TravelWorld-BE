"""
Module for defining custom filter sets for the UserReview model.

This module includes:
- ReviewFilter: A filter set for filtering user reviews based on package, activity, and booking.

Classes:
    - ReviewFilter: Filter set for the UserReview model.
"""
import django_filters
from api.models import UserReview


class ReviewFilter(django_filters.FilterSet):
    """
    Filter for various fields in the UserReview model.

    This filter set allows you to filter user reviews based on different criteria,
    including package, activity, and booking.

    Fields:
        package (CharFilter): Filters reviews by the associated package.
        activity (CharFilter): Filters reviews by the associated activity.
        booking (CharFilter): Filters reviews by the associated booking.
    """
    package = django_filters.CharFilter(field_name='package')
    activity = django_filters.CharFilter(field_name='activity')
    booking = django_filters.CharFilter(field_name='booking')

    class Meta:
        """
        Meta options for ReviewFilter.

        Attributes:
            model (api.models.UserReview): The model that this filter set is based on.
            fields (list): The list of fields that this filter set can filter on.
        """
        model = UserReview
        fields = ['package', 'activity', 'booking']
