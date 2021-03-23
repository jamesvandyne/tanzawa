from django.urls import path

from . import views

app_name = "wordpress"

urlpatterns = [
    path("upload/", views.TWordpressCreate.as_view(), name="t_wordpress_create"),
    path("", views.TWordpressListView.as_view(), name="t_wordpress_list"),
]
