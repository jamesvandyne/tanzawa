from django.urls import path

from . import views

urlpatterns = [
    path("files/", views.FilesList.as_view(), name="files"),
    path("files/<int:pk>", views.FileDetail.as_view(), name="file_detail"),
    path("files/<int:pk>/delete", views.FileDelete.as_view(), name="file_delete"),
]
