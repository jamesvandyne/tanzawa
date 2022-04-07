from data.files.models import TFile, TFilePost, TFormattedImage
from django.contrib import admin


class TFileAdmin(admin.ModelAdmin):
    list_display = ["filename", "point"]


admin.site.register(TFile, TFileAdmin)
admin.site.register(TFilePost)
admin.site.register(TFormattedImage)
