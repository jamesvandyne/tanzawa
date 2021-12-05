from django.contrib import admin

from .models import MStream, TStreamPost


class MStreamAdmin(admin.ModelAdmin):
    list_display = ("display_name", "slug", "get_visibility_display")

    def display_name(self, obj):
        return f"{obj.icon} {obj.name}"


admin.site.register(MStream, MStreamAdmin)
admin.site.register(TStreamPost)
