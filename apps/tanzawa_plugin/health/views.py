from django import http, urls
from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from django.utils import decorators as util_decorators
from django.views import generic

from . import application, forms, models


@util_decorators.method_decorator(auth_decorators.login_required, name="dispatch")
class Health(generic.TemplateView):
    """
    A view that displays charts and graphs for our health data.
    """

    template_name = "health/health.html"
    weight: models.Weight | None
    mood: models.Mood | None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.weight = models.Weight.objects.latest("measured_at")
        self.mood = models.Mood.objects.latest("measured_at")

    def get_context_data(self, **kwargs):
        return super().get_context_data(page_title="Health", nav="health", weight=self.weight, mood=self.mood)


@util_decorators.method_decorator(auth_decorators.login_required, name="dispatch")
class AddDailyHealth(generic.FormView):
    form_class = forms.DailyCheckinForm
    template_name = "health/add.html"
    success_url = urls.reverse_lazy("plugin_health_admin:health")
    object = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(page_title="Daily Health", nav="health")

    def form_valid(self, form):
        application.save_daily_health(
            weight=form.cleaned_data["weight"],
            unit=form.cleaned_data["weight_unit"],
            mood=form.cleaned_data["mood"],
        )
        messages.success(self.request, "Recorded your daily health measurements.")
        return super().form_valid(form)


@auth_decorators.login_required
def graph_api(request) -> http.JsonResponse:
    points = models.Weight.objects.order_by("-measured_at")[:10]
    return http.JsonResponse(
        data={
            "labels": [point.measured_at.date() for point in reversed(points)],
            "weight": [point.measurement for point in reversed(points)],
        }
    )
