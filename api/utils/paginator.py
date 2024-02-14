#Pagination
from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size = 5  # Number of objects to return per page
    page_size_query_param = 'page_size'  # Custom query parameter to specify page size
    max_page_size = 100 