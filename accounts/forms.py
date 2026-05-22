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
        fields = ("email", "phone_number")


class ResponsePreferenceForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("response_length", "response_tone", "show_theory_basis")
        labels = {
            "response_length": "回答長度",
            "response_tone": "回答語氣",
            "show_theory_basis": "在適合時顯示心理學理論依據",
        }
        help_texts = {
            "response_length": "短回答偏向 80-140 字，適合想先被接住；長回答偏向 260-450 字，會多做脈絡整理與下一步拆解。",
            "response_tone": "溫柔陪伴會更像有人在旁邊接住你；直接清楚會更快切重點；深入反思會多幫你整理模式與關係脈絡。",
            "show_theory_basis": "開啟後，回答會在自然情況下補一小段「我這裡用到的概念」，例如 CBT、情緒命名、依附與界線，不會冒充正式診斷。",
        }


class VisualPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("preferred_theme_color",)
        labels = {"preferred_theme_color": "主題色"}


class AdvancedSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("allow_memory_summaries", "allow_inline_media_cards")
        labels = {
            "allow_memory_summaries": "允許系統整理長期聊天摘要",
            "allow_inline_media_cards": "允許在聊天中產生站內影音與圖片卡片",
        }
        help_texts = {
            "allow_memory_summaries": "開啟後，同一聊天室會更容易延續前文；關閉後，長期脈絡會更少被使用。",
            "allow_inline_media_cards": "開啟後，當你聊到音樂、影片、偶像或興趣時，系統可以附上站內播放或搜尋卡片。",
        }
