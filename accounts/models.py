from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    THEME_CHOICES = [
        ("teal", "沉靜綠"),
        ("indigo", "深海藍"),
        ("rose", "暖玫瑰"),
        ("slate", "專注灰"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    preferred_theme_color = models.CharField(max_length=16, choices=THEME_CHOICES, default="teal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"
