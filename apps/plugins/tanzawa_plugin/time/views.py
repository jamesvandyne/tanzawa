from django.http import HttpResponse
from django.conf import settings


def timezone(request):
    return HttpResponse(request, settings.TIME_ZONE)
