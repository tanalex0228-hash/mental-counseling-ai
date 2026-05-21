from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views as account_views
from . import views


urlpatterns = [
    path("", views.chat_home, name="chat_home"),
    path("c/<int:room_id>/", views.chat_home, name="room"),
    path("api/chat/", views.chat_api, name="chat_api"),
    path("api/rooms/", views.room_list_api, name="room_list_api"),
    path("api/tools/youtube-search/", views.youtube_search_api, name="youtube_search_api"),
    path("api/tools/companion-search/", views.companion_search_api, name="companion_search_api"),
    path("register/", account_views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("settings/theme/", views.update_theme, name="update_theme"),
    path("conversation/new/", views.new_conversation, name="new_conversation"),
]
