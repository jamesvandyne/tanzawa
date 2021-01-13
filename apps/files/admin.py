from django.contrib import admin

from .models import TFile, TFilePost, TFormattedImage

admin.site.register(TFile)
admin.site.register(TFilePost)
admin.site.register(TFormattedImage)
