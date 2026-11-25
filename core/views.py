from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from accounts.models import User
from django.shortcuts import render
from accounts.models import User

def home(request):
    """Home page view with latest courses"""
    
    try:
        from quests.models import Quest
        total_quests = Quest.objects.filter(is_active=True).count()
    except ImportError:
        total_quests = 0

    try:
        from farms.models import Farm
        total_farms = Farm.objects.count()
    except ImportError:
        total_farms = 0

    try:
        from gamification.models import Badge
        total_badges = Badge.objects.filter(is_active=True).count()
    except ImportError:
        total_badges = 0

    try:
        from courses.models import Course,Certificate
        # Latest 6 published courses ordered by creation date descending
        latest_courses = Course.objects.filter(status='published').order_by('-created_at')[:6]
        total_courses = Course.objects.filter(status='published').count()
        total_certificates = Certificate.objects.count()

    except ImportError:
        total_courses = 0
        latest_courses = []
        total_certificates = 0

    # Optional: load testimonials if you have such model
    try:
        from core.models import Testimonial
        testimonials = Testimonial.objects.filter(is_published=True)[:6]
    except ImportError:
        testimonials = []

    stats = {
        'total_learners': User.objects.count(),
        'total_farms': total_farms,
        'total_quests': total_quests,
        'total_badges': total_badges,
        'total_courses': total_courses,
        'total_certificates': total_certificates,
    # add other homepage stats here if needed
        }
    context = {
        'stats': stats,
        'latest_courses': latest_courses,
        'testimonials': testimonials,
        }


    return render(request, 'core/home.html', context)


@login_required
def dashboard(request):
    """User dashboard view"""
    user = request.user

    # User's farms
    try:
        from farms.models import Farm
        user_farms = Farm.objects.filter(owner=user)[:5]
        total_farms = Farm.objects.filter(owner=user).count()
    except:
        user_farms = []
        total_farms = 0

    # User's quest completions
    try:
        from quests.models import QuestCompletion, Quest
        completed_quests = QuestCompletion.objects.filter(user=user, is_completed=True).count()
        completed_quest_ids = QuestCompletion.objects.filter(user=user, is_completed=True).values_list('quest_id', flat=True)
        available_quests = Quest.objects.filter(is_active=True).exclude(id__in=completed_quest_ids)[:5]
        in_progress_quests = QuestCompletion.objects.filter(user=user, is_completed=False).count()
    except:
        completed_quests = 0
        available_quests = []
        in_progress_quests = 0

    # User's badges and achievements
    try:
        from gamification.models import UserBadge, Achievement
        user_badges = UserBadge.objects.filter(user=user).select_related('badge')[:6]
        recent_achievements = Achievement.objects.filter(user=user)[:5]
        total_badges = UserBadge.objects.filter(user=user).count()
    except:
        user_badges = []
        recent_achievements = []
        total_badges = 0

    # User's courses
    try:
        from courses.models import CourseEnrollment
        enrolled_courses = CourseEnrollment.objects.filter(user=user).select_related('course')[:5]
        completed_courses = enrolled_courses.filter(progress=100).count()
        in_progress_courses = enrolled_courses.filter(progress__gt=0, progress__lt=100).count()
    except:
        enrolled_courses = []
        completed_courses = 0
        in_progress_courses = 0

    # Leaderboard position
    leaderboard_position = user.get_leaderboard_position()

    # Recent points history
    try:
        from gamification.models import PointsHistory
        recent_points = PointsHistory.objects.filter(user=user)[:5]
    except:
        recent_points = []

    context = {
        'user_farms': user_farms,
        'total_farms': total_farms,
        'completed_quests_count': completed_quests,
        'in_progress_quests_count': in_progress_quests,
        'available_quests': available_quests,
        'user_badges': user_badges,
        'total_badges': total_badges,
        'recent_achievements': recent_achievements,
        'enrolled_courses': enrolled_courses,
        'completed_courses_count': completed_courses,
        'in_progress_courses_count': in_progress_courses,
        'leaderboard_position': leaderboard_position,
        'recent_points': recent_points,
        'total_users': User.objects.count(),
    }
    return render(request, 'core/dashboard.html', context)


