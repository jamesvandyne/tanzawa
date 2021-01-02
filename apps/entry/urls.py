from django.urls import path
from . import views

urlpatterns = [
    path('status/create', views.status_create, name="status_create"),
    path('status/', views.status_list, name="status_list"),
]
