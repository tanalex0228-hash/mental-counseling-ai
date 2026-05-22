from django.urls import path

from . import views


urlpatterns = [
    path("settings/", views.settings_view, name="settings"),
    path("settings/profile/", views.settings_view, {"tab": "profile"}, name="settings_profile"),
    path("settings/response/", views.settings_view, {"tab": "response"}, name="settings_response"),
    path("settings/visual/", views.settings_view, {"tab": "visual"}, name="settings_visual"),
    path("settings/advanced/", views.settings_view, {"tab": "advanced"}, name="settings_advanced"),
    path("settings/security/", views.settings_view, {"tab": "security"}, name="settings_security"),
    path("settings/profile/update/", views.update_profile, name="update_profile"),
    path("settings/response/update/", views.update_response_preferences, name="update_response_preferences"),
    path("settings/visual/update/", views.update_visual_preferences, name="update_visual_preferences"),
    path("settings/advanced/update/", views.update_advanced_settings, name="update_advanced_settings"),
    path("settings/password/", views.change_password, name="change_password"),
]
