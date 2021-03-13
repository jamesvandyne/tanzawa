from django.contrib import admin

from .models import TEntry, TReply, TLocation

admin.site.register(TEntry)
admin.site.register(TReply)
admin.site.register(TLocation)
