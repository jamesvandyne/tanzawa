from django.contrib import admin

from .models import TWebmention, TWebmentionSend


class TWebmentionSendAdmin(admin.ModelAdmin):
    list_display = ("target", "dt_sent", "success", "t_post")


admin.site.register(TWebmention)
admin.site.register(TWebmentionSend, TWebmentionSendAdmin)
