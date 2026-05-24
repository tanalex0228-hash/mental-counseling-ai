from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    THEME_CHOICES = [
        ("teal", "沉靜綠"),
        ("indigo", "深海藍"),
        ("rose", "暖玫瑰"),
        ("slate", "專注灰"),
    ]
    RESPONSE_LENGTH_CHOICES = [
        ("balanced", "剛剛好"),
        ("short", "短回答"),
        ("long", "長回答"),
    ]
    TONE_CHOICES = [
        ("warm", "溫柔陪伴"),
        ("direct", "直接清楚"),
        ("reflective", "深入反思"),
    ]
    FONT_SCALE_CHOICES = [
        ("small", "小"),
        ("normal", "標準"),
        ("large", "大"),
    ]
    DENSITY_CHOICES = [
        ("cozy", "舒適"),
        ("compact", "緊湊"),
        ("spacious", "寬鬆"),
    ]
    EFFECT_CHOICES = [
        ("none", "無特效"),
        ("snow", "雪花"),
        ("bubbles", "泡泡"),
        ("rain", "下雨"),
        ("sunlight", "陽光光影"),
    ]
    BUBBLE_STYLE_CHOICES = [
        ("standard", "標準"),
        ("soft", "柔和圓角"),
        ("glass", "玻璃感"),
        ("sharp", "俐落方角"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    preferred_theme_color = models.CharField(max_length=16, choices=THEME_CHOICES, default="teal")
    custom_accent_color = models.CharField(max_length=7, default="#188977")
    font_scale = models.CharField(max_length=16, choices=FONT_SCALE_CHOICES, default="normal")
    chat_density = models.CharField(max_length=16, choices=DENSITY_CHOICES, default="cozy")
    visual_effect = models.CharField(max_length=16, choices=EFFECT_CHOICES, default="none")
    bubble_style = models.CharField(max_length=16, choices=BUBBLE_STYLE_CHOICES, default="standard")
    dark_mode = models.BooleanField(default=False)
    cyberpunk_mode = models.BooleanField(default=False)
    response_length = models.CharField(max_length=16, choices=RESPONSE_LENGTH_CHOICES, default="balanced")
    response_tone = models.CharField(max_length=24, choices=TONE_CHOICES, default="warm")
    show_theory_basis = models.BooleanField(default=False)
    allow_memory_summaries = models.BooleanField(default=True)
    allow_inline_media_cards = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"
