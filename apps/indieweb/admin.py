from django.contrib import admin

from .models import TWebmention, TWebmentionSend

admin.site.register(TWebmention)
admin.site.register(TWebmentionSend)
