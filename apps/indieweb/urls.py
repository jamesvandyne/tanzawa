from django.urls import path
from . import views

urlpatterns = [
    path('micropub/', views.micropub, name="micropub"),
]
