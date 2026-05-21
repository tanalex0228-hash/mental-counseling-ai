from django.urls import path

from . import views


urlpatterns = [
    path("settings/", views.settings_view, name="settings"),
    path("settings/profile/", views.update_profile, name="update_profile"),
    path("settings/password/", views.change_password, name="change_password"),
]
