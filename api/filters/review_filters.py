import django_filters
from api.models import UserReview


class ReviewFilter(django_filters.FilterSet):
    package = django_filters.CharFilter(field_name='package')
    activity = django_filters.CharFilter(field_name='activity')

    class Meta:
        model = UserReview
        fields = ['package','activity']