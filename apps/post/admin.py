from django.contrib import admin

from .models import MPostKind, TPost

admin.site.register(TPost)
admin.site.register(MPostKind)
