from django.urls import path
from interfaces.dashboard.top import views

app_name = "post"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]
