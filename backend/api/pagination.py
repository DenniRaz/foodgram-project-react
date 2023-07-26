from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """
    A simple style that supports page numbers and page size
    as query parameters.
    """

    page_size_query_param = 'limit'
