from django.urls import path
from . import views

urlpatterns = [
    path('status/create/', views.status_create, name="status_create"),
    path('status/<int:pk>/', views.status_detail, name="status_detail"),
    path('status/<int:pk>/edit/', views.status_edit, name="status_edit"),
    path('status/<int:pk>/delete/', views.status_delete, name="status_delete"),
    path('status/', views.status_list, name="status_list"),
]
