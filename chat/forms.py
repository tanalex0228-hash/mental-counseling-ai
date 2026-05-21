from django import forms

from accounts.models import UserProfile


class ThemeForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("preferred_theme_color",)
