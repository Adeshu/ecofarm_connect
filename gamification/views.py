from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Badge, UserBadge, Achievement, PointsHistory, Leaderboard
from accounts.models import User
from django.db.models import Count

def leaderboard(request):
    board_type = request.GET.get('type', 'overall')

    if board_type == 'overall':
        top_users = User.objects.annotate(
            farms_count=Count('farms')  # Adjust if your FK related_name is different
        ).filter(total_points__gt=0).order_by('-total_points', '-date_joined')[:50]

    elif board_type == 'monthly':
        start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_points = PointsHistory.objects.filter(
            created_at__gte=start_date,
            points_change__gt=0,
        ).values('user').annotate(
            monthly_total=Count('points_change')
        ).order_by('-monthly_total')[:50]

        user_ids = [item['user'] for item in monthly_points]
        top_users = User.objects.filter(id__in=user_ids).order_by('-total_points')

    else:
        top_users = User.objects.annotate(
            farms_count=Count('farms')
        ).filter(total_points__gt=0).order_by('-total_points')[:50]

    context = {
        'top_users': top_users,
        'current_type': board_type,
        'user_position': request.user.get_leaderboard_position() if request.user.is_authenticated else None,
    }

    return render(request, 'gamification/leaderboard.html', context)

def badges(request):
    """All available badges"""
    badges = Badge.objects.filter(is_active=True).order_by('points_required', 'name')

    # Get user's earned badges
    earned_badge_ids = []
    if request.user.is_authenticated:
        earned_badge_ids = UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True)

    # Filter by category
    category = request.GET.get('category')
    if category:
        badges = badges.filter(category=category)

    # Filter by rarity
    rarity = request.GET.get('rarity')
    if rarity:
        badges = badges.filter(rarity=rarity)

    context = {
        'badges': badges,
        'earned_badge_ids': earned_badge_ids,
        'current_category': category,
        'current_rarity': rarity,
        'categories': Badge.BADGE_TYPE_CHOICES,
        'rarities': [
            ('common', 'Common'),
            ('uncommon', 'Uncommon'),
            ('rare', 'Rare'),
            ('epic', 'Epic'),
            ('legendary', 'Legendary'),
        ],
    }
    return render(request, 'gamification/badges.html', context)

@login_required
def my_badges(request):
    """User's earned badges"""
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge').order_by('-earned_at')

    # Filter by category
    category = request.GET.get('category')
    if category:
        user_badges = user_badges.filter(badge__category=category)

    context = {
        'user_badges': user_badges,
        'current_category': category,
        'categories': Badge.BADGE_TYPE_CHOICES,
    }
    return render(request, 'gamification/my_badges.html', context)

@login_required
def my_achievements(request):
    """User's achievements"""
    achievements = Achievement.objects.filter(user=request.user).order_by('-achieved_at')

    # Pagination
    paginator = Paginator(achievements, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'gamification/my_achievements.html', context)

@login_required
def points_history(request):
    """User's points history"""
    history = PointsHistory.objects.filter(user=request.user).order_by('-created_at')

    # Filter by type
    point_type = request.GET.get('type')
    if point_type:
        history = history.filter(point_type=point_type)

    # Pagination
    paginator = Paginator(history, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'current_type': point_type,
        'point_types': PointsHistory.POINT_TYPES,
    }
    return render(request, 'gamification/points_history.html', context)

def user_profile_public(request, user_id):
    """Public user profile with gamification stats"""
    user = get_object_or_404(User, id=user_id)

    # Get user's badges
    user_badges = UserBadge.objects.filter(user=user).select_related('badge')[:12]

    # Get recent achievements
    recent_achievements = Achievement.objects.filter(user=user)[:10]

    # Get stats
    total_achievements = Achievement.objects.filter(user=user).count()
    total_badges = UserBadge.objects.filter(user=user).count()

    context = {
        'profile_user': user,
        'user_badges': user_badges,
        'recent_achievements': recent_achievements,
        'total_achievements': total_achievements,
        'total_badges': total_badges,
        'leaderboard_position': user.get_leaderboard_position(),
    }
    return render(request, 'gamification/user_profile.html', context)


