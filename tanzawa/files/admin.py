from django.contrib import admin

from .models import TFile, TFilePost, TFormattedImage


class TFileAdmin(admin.ModelAdmin):
    list_display = ["filename", "point"]


admin.site.register(TFile, TFileAdmin)
admin.site.register(TFilePost)
admin.site.register(TFormattedImage)
