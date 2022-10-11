from typing import Any

from django.conf import settings
from django.core.paginator import Paginator


def get_page_obj(request, object_list: Any):
    paginator = Paginator(object_list, settings.POST_ON_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
