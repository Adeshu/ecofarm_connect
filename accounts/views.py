# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.urls import reverse

from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    UserProfileForm,
    ProfileUpdateForm,
)
from .models import User, UserProfile
from gamification.models import Achievement, PointsHistory


def register(request):
    """User registration view"""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()

                # Create linked profile
                UserProfile.objects.create(user=user)

                # Award registration bonus and create related achievements
                user.total_points += 50
                user.update_level()
                user.save()

                Achievement.objects.create(
                    user=user,
                    title="Welcome to Sustainable Farming!",
                    description="Successfully registered and joined the community",
                    points_earned=50,
                )
                PointsHistory.objects.create(
                    user=user,
                    points_change=50,
                    point_type="bonus",
                    description="Registration bonus",
                )

                login(request, user)
                messages.success(request, "Your account has been created. You can log in now.")
                return redirect("core:dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name()}!")
            return redirect("core:dashboard")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})


@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("core:home")


@login_required
def profile(request):
    """View logged-in user's profile"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    leaderboard_position = user.get_leaderboard_position()

    return render(request, "accounts/profile.html", {
        "user": user,
        "profile": profile,
        "leaderboard_position": leaderboard_position,
    })

@login_required
def profile_edit(request):
    """Edit user and profile info"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = ProfileUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)  # Include request.FILES here

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = ProfileUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        "form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "accounts/profile_edit.html", context)


def user_detail(request, user_id):
    """Public view of user's profile"""
    user = get_object_or_404(User, id=user_id)
    profile = getattr(user, "profile", None)

    # Optional stats (quest, course completion, farms, badges)
    from quests.models import QuestCompletion
    from courses.models import CourseEnrollment
    from farms.models import Farm
    from gamification.models import UserBadge

    completed_quests = QuestCompletion.objects.filter(user=user, is_completed=True).count()
    completed_courses = CourseEnrollment.objects.filter(user=user, progress=100).count()
    public_farms = Farm.objects.filter(owner=user)[:3]
    recent_badges = UserBadge.objects.filter(user=user).select_related("badge")[:6]

    return render(request, "accounts/user_detail.html", {
        "profile_user": user,
        "profile": profile,
        "completed_quests": completed_quests,
        "completed_courses": completed_courses,
        "public_farms": public_farms,
        "recent_badges": recent_badges,
        "leaderboard_position": user.get_leaderboard_position(),
    })
