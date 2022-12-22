from django.contrib import admin

from data.entry.models import (
    TBookmark,
    TCheckin,
    TEntry,
    TLocation,
    TReply,
    TSyndication,
)

admin.site.register(TEntry)
admin.site.register(TReply)
admin.site.register(TLocation)
admin.site.register(TBookmark)
admin.site.register(TCheckin)
admin.site.register(TSyndication)
