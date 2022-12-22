from django.contrib import admin

from data.wordpress.models import (
    TCategory,
    TPostFormat,
    TPostKind,
    TWordpress,
    TWordpressAttachment,
    TWordpressPost,
)

admin.site.register(TWordpress)
admin.site.register(TCategory)
admin.site.register(TPostFormat)
admin.site.register(TPostKind)
admin.site.register(TWordpressPost)


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("guid", "uuid")


admin.site.register(TWordpressAttachment, AttachmentAdmin)
