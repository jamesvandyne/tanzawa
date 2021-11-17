from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, resolve_url
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import ProcessFormView, SingleObjectTemplateResponseMixin
from trips.forms import TLocationModelForm, TTripModelForm
from trips.models import TTrip
from turbo_response import redirect_303


@method_decorator(login_required, "dispatch")
class TripListView(ListView):
    def get_queryset(self):
        return TTrip.objects.visible_for_user(self.request.user.id)

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, nav="trips", **kwargs)


class ProcessNamedFormMixin(SingleObjectTemplateResponseMixin, ContextMixin, ProcessFormView):
    redirect_url = ""
    template_name = ""

    def get_named_forms_kwargs(self, form_name: str):
        return {"prefix": "location"}

    def get_named_forms(self):
        return {
            "location": TLocationModelForm(self.request.POST or None, **self.get_named_forms_kwargs("location")),
        }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if "named_forms" not in context:
            context["named_forms"] = self.get_named_forms()
        return context

    def form_valid(self, form, named_forms=None):
        with transaction.atomic():
            instance = form.save()
            for named_form in named_forms.values():
                named_form.prepare_data(instance)
                named_form.save()
        return redirect_303(resolve_url(self.redirect_url, pk=instance.pk))

    def form_invalid(self, form, named_forms=None):
        context = self.get_context_data(form=form, named_forms=named_forms)
        return render(self.request, self.template_name, context=context, status=422)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()
        form = self.get_form()
        named_forms = self.get_named_forms()

        if form.is_valid() and all((named_form.is_valid() for named_form in named_forms.values())):
            return self.form_valid(form, named_forms)
        else:
            return self.form_invalid(form, named_forms)


@method_decorator(login_required, "dispatch")
class CreateTripView(ProcessNamedFormMixin, CreateView):
    model = TTrip
    form_class = TTripModelForm
    template_name = "trips/ttrip_create.html"
    redirect_url = "trip_edit"
    extra_context = {"nav": "trips", "page_title": "Create Trip"}

    def get_object(self, *args, **kwargs):
        return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["p_author"] = self.request.user
        return kwargs


@method_decorator(login_required, "dispatch")
class UpdateTripView(ProcessNamedFormMixin, UpdateView):
    form_class = TTripModelForm
    template_name = "trips/ttrip_update.html"
    extra_context = {"nav": "trips", "page_title": "Update Trip"}
    redirect_url = "trip_edit"

    def get_queryset(self):
        return TTrip.objects.visible_for_user(self.request.user.id)

    def get_named_forms_kwargs(self, form_name: str):
        return {"prefix": "location", "instance": self.get_object().t_trip_location.first()}


@method_decorator(login_required, "dispatch")
class DeleteTripView(DeleteView):
    def get_queryset(self):
        return TTrip.objects.visible_for_user(self.request.user.id)

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(*args, nav="trips", **kwargs)
