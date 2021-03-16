from django.contrib import admin

from .models import TEntry, TReply, TLocation, TCheckin, TBookmark, TSyndication

admin.site.register(TEntry)
admin.site.register(TReply)
admin.site.register(TLocation)
admin.site.register(TBookmark)
admin.site.register(TCheckin)
admin.site.register(TSyndication)
