from django.urls import path
from . import views

urlpatterns = [
    path('create', views.entry, name="entry_create"),
    path('', views.entries, name="entry_list"),
]
