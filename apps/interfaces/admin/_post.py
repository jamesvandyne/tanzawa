from django.contrib import admin

from data.post.models import MPostKind, TPost

admin.site.register(TPost)
admin.site.register(MPostKind)
