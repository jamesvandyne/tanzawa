from django.contrib import admin

from .models import TWordpress, TPostKind, TCategory, TPostFormat

admin.site.register(TWordpress)
admin.site.register(TCategory)
admin.site.register(TPostFormat)
admin.site.register(TPostKind)
