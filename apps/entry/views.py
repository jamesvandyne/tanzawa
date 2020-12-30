from django.shortcuts import render

from . import forms
from . import models


def entry(request):
    form = forms.CreateEntryForm()
    context = {
        'form': form
    }
    return render(request, "entry/entry_create.html", context=context)


def entries(request):
    objects = models.TEntry.objects.all()
    return render(request, "entry/entry_list.html", context={"objects": objects})
