from data.settings.models import MSiteSettings
from django import forms
from django.contrib import admin
from domain.settings import queries


class MSiteSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = MSiteSettings
        fields = "__all__"

    theme = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["theme"].choices = queries.get_theme_choices()


class MSiteSettingsAdmin(admin.ModelAdmin):
    form = MSiteSettingsAdminForm


admin.site.register(MSiteSettings, MSiteSettingsAdmin)
