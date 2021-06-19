from django.views.generic import FormView

from .forms import FirstRunForm


class FirstRun(FormView):
    form_class = FirstRunForm
    template_name = "settings/first_run.html"
