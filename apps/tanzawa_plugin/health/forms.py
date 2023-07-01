from django import forms, urls

from . import constants


class DailyCheckinForm(forms.Form):
    weight = forms.DecimalField(
        label="How much do you weigh?",
        help_text="Be honest. Nobody can see this but you.",
        widget=forms.NumberInput(attrs={"inputmode": "decimal"}),
    )
    weight_unit = forms.ChoiceField(
        choices=constants.WeightUnitChoices.choices,
        initial=constants.WeightUnitChoices.KILOGRAMS,
        widget=forms.RadioSelect(attrs={"class": "peer appearance-none hidden"}),
    )
    mood = forms.ChoiceField(
        choices=constants.EmojiMoodChoices.choices,
        initial=constants.MoodChoices.NEUTRAL,
        label="How do you feel?",
        widget=forms.RadioSelect(attrs={"class": "peer appearance-none hidden"}),
        help_text="For real. You're not fooling anybody.",
    )


class WeightGraph(forms.Form):
    duration = forms.ChoiceField(
        choices=constants.GraphDuration.choices,
        initial=constants.GraphDuration.SIX_WEEKS,
        widget=forms.Select(
            attrs={"hx-get": urls.reverse_lazy("plugin_health_admin:weight_graph"), "hx-target": "#chart"}
        ),
        required=False,
    )
