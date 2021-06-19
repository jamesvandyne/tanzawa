from django import forms

from core.forms import TCharField


class FirstRunForm(forms.Form):

    username = TCharField(label_suffix="", help_text="")
    first_name = TCharField(label_suffix="", help_text="", label="First")
    last_name = TCharField(label_suffix="", help_text="", required=False, label="Last")
    password = TCharField(widget=forms.PasswordInput(attrs={"class": "input-field"}), label="Strong Password", label_suffix="",
                          help_text="Minimum 8 characters. Mix numbers and letters, please.")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "input-field", "placeholder": "hello@example.com"}), label_suffix="")
    blog_title = TCharField(initial="Tanzawa", label="Title", label_suffix="")
    blog_subtitle = TCharField(required=False, label="Subtitle", label_suffix="")

