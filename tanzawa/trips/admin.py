from django.contrib import admin

from .models import TTrip, TTripLocation, TTripPost

admin.site.register(TTrip)
admin.site.register(TTripPost)
admin.site.register(TTripLocation)
