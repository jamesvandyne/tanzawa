from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView
from django import forms
from django.http import Http404
from turbo_response import redirect_303

from .models import TWordpress, TCategory
from .forms import WordpressUploadForm, TCategoryModelForm


class TWordpressListView(ListView):

    model = TWordpress
    allow_empty = False

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect_303("wordpress:t_wordpress_create")


class TWordpressCreate(CreateView):
    form_class = WordpressUploadForm
    template_name = "wordpress/wordpress_create.html"


def category_mappings(request, pk):
    t_wordpress = get_object_or_404(TWordpress, pk=pk)
    TCategoryModelFormSet = forms.modelformset_factory(TCategory, TCategoryModelForm,
                                                       extra=0)

    formset = TCategoryModelFormSet(initial=[])
    context = {
        "t_wordpress": t_wordpress,
        "formset": formset,
    }
    return render(request, "wordpress/tcategory_mapping.html", context=context)
