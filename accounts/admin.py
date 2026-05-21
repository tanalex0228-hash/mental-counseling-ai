from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "phone_number", "preferred_theme_color", "updated_at")
    search_fields = ("user__username", "email", "phone_number")
