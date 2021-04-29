from django.urls import path

from . import views

urlpatterns = [
    path("files/", views.FilesList.as_view(), name="files"),

]
