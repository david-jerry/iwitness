from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Paginating the queryset to limit the amount fo request to a page so as not to sow the request down

    example:
        htpps://www.iwitnessreporter.news/api/v1/other-links/?page_size=5

    Args:
        PageNumberPagination (Object Class): RestFramework default pagination
    """

    page_size = 10
    page_query_param = "page"
    max_page_size = 100
