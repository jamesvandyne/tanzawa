from django import forms
from django.conf import settings
from django.contrib import admin

from .models import MSiteSettings

THEME_CHOICES = [
    ["", "Tanzawa"],
] + [(theme, theme.title()) for theme in settings.THEMES]


class MSiteSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = MSiteSettings
        fields = "__all__"

    theme = forms.ChoiceField(choices=THEME_CHOICES, required=False)


class MSiteSettingsAdmin(admin.ModelAdmin):
    form = MSiteSettingsAdminForm


admin.site.register(MSiteSettings, MSiteSettingsAdmin)
