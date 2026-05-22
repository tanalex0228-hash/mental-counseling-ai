from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import AdvancedSettingsForm, ProfileSettingsForm, RegisterForm, ResponsePreferenceForm, VisualPreferenceForm
from .models import UserProfile


def ensure_profile(user):
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={"email": user.email},
    )
    return profile


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()
            UserProfile.objects.create(
                user=user,
                email=form.cleaned_data["email"],
                phone_number=form.cleaned_data.get("phone_number", ""),
            )
            login(request, user)
            return redirect("chat_home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def settings_view(request, tab=None):
    profile = ensure_profile(request.user)
    profile_form = ProfileSettingsForm(instance=profile)
    response_form = ResponsePreferenceForm(instance=profile)
    visual_form = VisualPreferenceForm(instance=profile)
    advanced_form = AdvancedSettingsForm(instance=profile)
    password_form = PasswordChangeForm(request.user)
    active_tab = tab or request.GET.get("tab", "profile")
    return render(
        request,
        "accounts/settings.html",
        {
            "profile": profile,
            "profile_form": profile_form,
            "response_form": response_form,
            "visual_form": visual_form,
            "advanced_form": advanced_form,
            "password_form": password_form,
            "active_tab": active_tab,
        },
    )


@require_POST
@login_required
def update_profile(request):
    profile = ensure_profile(request.user)
    form = ProfileSettingsForm(request.POST, instance=profile)
    if form.is_valid():
        updated_profile = form.save()
        request.user.email = updated_profile.email
        request.user.save(update_fields=["email"])
        messages.success(request, "設定已儲存。")
    else:
        messages.error(request, "設定格式有誤，請再檢查一次。")
    return redirect(request.POST.get("next") or "settings")


@require_POST
@login_required
def update_response_preferences(request):
    profile = ensure_profile(request.user)
    form = ResponsePreferenceForm(request.POST, instance=profile)
    if form.is_valid():
        form.save()
        messages.success(request, "回答偏好已儲存。")
    else:
        messages.error(request, "回答偏好格式有誤，請再檢查一次。")
    return redirect("settings_response")


@require_POST
@login_required
def update_visual_preferences(request):
    profile = ensure_profile(request.user)
    form = VisualPreferenceForm(request.POST, instance=profile)
    if form.is_valid():
        form.save()
        messages.success(request, "視覺偏好已儲存。")
    else:
        messages.error(request, "視覺偏好格式有誤，請再檢查一次。")
    return redirect("settings_visual")


@require_POST
@login_required
def update_advanced_settings(request):
    profile = ensure_profile(request.user)
    form = AdvancedSettingsForm(request.POST, instance=profile)
    if form.is_valid():
        form.save()
        messages.success(request, "高級設定已儲存。")
    else:
        messages.error(request, "高級設定格式有誤，請再檢查一次。")
    return redirect("settings_advanced")


@require_POST
@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "密碼已更新。")
    else:
        messages.error(request, "密碼更新失敗，請確認目前密碼與新密碼格式。")
    return redirect("settings_security")
