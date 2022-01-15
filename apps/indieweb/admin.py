from django.contrib import admin

from .models import (
    MMicropubScope,
    TRelMe,
    TToken,
    TTokenMicropubScope,
    TWebmention,
    TWebmentionSend,
)


class TWebmentionSendAdmin(admin.ModelAdmin):
    list_display = ("target", "dt_sent", "success", "t_post")


admin.site.register(TWebmention)
admin.site.register(TWebmentionSend, TWebmentionSendAdmin)
admin.site.register(TToken)
admin.site.register(MMicropubScope)
admin.site.register(TTokenMicropubScope)
admin.site.register(TRelMe)
