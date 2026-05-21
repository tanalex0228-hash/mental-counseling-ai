from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email", required=True)
    phone_number = forms.CharField(label="電話", required=False, max_length=32)

    class Meta:
        model = User
        fields = ("username", "email", "phone_number", "password1", "password2")


class ProfileSettingsForm(forms.ModelForm):
    email = forms.EmailField(label="Email", required=False)

    class Meta:
        model = UserProfile
        fields = ("email", "phone_number", "preferred_theme_color")
