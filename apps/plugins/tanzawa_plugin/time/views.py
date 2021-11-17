from django.conf import settings
from django.http import HttpResponse


def timezone(request):
    return HttpResponse(request, settings.TIME_ZONE)
