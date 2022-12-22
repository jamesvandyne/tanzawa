from django import urls
from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from django.utils import decorators as util_decorators
from django.views import generic

from . import application, forms, models


@util_decorators.method_decorator(auth_decorators.login_required, name="dispatch")
class UpdateNowAdmin(generic.FormView, generic.edit.SingleObjectMixin):
    form_class = forms.UpdateNow
    template_name = "now/edit.html"
    success_url = urls.reverse_lazy("plugin_now_admin:update_now")
    object = None

    def get_object(self, queryset=None) -> models.TNow:
        if not self.object:
            self.object = models.TNow.objects.first() or models.TNow.objects.create()
        return self.object

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {"content": self.get_object().content}
        return kwargs

    def get_context_data(self, **kwargs):
        return super().get_context_data(page_title="Edit Now", nav="plugins")

    def form_valid(self, form):
        application.update_now(t_now=self.object, content=form.cleaned_data["content"])
        messages.success(self.request, "Updated Now")
        return super().form_valid(form)


class PublicViewNow(generic.TemplateView):
    template_name = "now/now.html"

    def dispatch(self, request, *args, **kwargs):

        self.now: models.TNow | None = models.TNow.objects.first()
        if not self.now:
            self.now = models.TNow.objects.create()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(page_title="Now", nav="now", object=self.now)
