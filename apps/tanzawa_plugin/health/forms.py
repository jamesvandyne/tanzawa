from django import forms

from . import constants


class DailyCheckinForm(forms.Form):
    weight = forms.DecimalField(label="How much do you weigh?", help_text="Be honest. Nobody can see this but you.")
    weight_unit = forms.ChoiceField(
        choices=constants.WeightUnitChoices.choices,
        initial=constants.WeightUnitChoices.KILOGRAMS,
        widget=forms.RadioSelect(attrs={"class": "peer appearance-none hidden"}),
    )
    mood = forms.ChoiceField(
        choices=(
            (constants.MoodChoices.NEGATIVE, "☹️"),
            (constants.MoodChoices.NEUTRAL, "😐"),
            (constants.MoodChoices.POSITIVE, "😀"),
        ),
        initial=constants.MoodChoices.NEUTRAL,
        label="How do you feel?",
        widget=forms.RadioSelect(attrs={"class": "peer appearance-none hidden"}),
        help_text="For real. You're not fooling anybody.",
    )
