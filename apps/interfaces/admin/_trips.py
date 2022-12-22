from django.contrib import admin

from data.trips import models

admin.site.register(models.TTrip)
admin.site.register(models.TTripPost)
admin.site.register(models.TTripLocation)
