from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import ProfileSettingsForm, RegisterForm
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
def settings_view(request):
    profile = ensure_profile(request.user)
    profile_form = ProfileSettingsForm(instance=profile)
    password_form = PasswordChangeForm(request.user)
    return render(
        request,
        "accounts/settings.html",
        {"profile": profile, "profile_form": profile_form, "password_form": password_form},
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
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "密碼已更新。")
    else:
        messages.error(request, "密碼更新失敗，請確認目前密碼與新密碼格式。")
    return redirect("settings")
