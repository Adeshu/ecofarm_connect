from .models import Badge, UserBadge

def award_badges_for_quest_completion(user, quest_id):
    badges = Badge.objects.filter(type='quest', quest_id=str(quest_id), is_active=True)
    for badge in badges:
        UserBadge.objects.get_or_create(user=user, badge=badge)

def award_badges_for_course_completion(user, course_id, score=None):
    badges = Badge.objects.filter(type='course', course_id=str(course_id), is_active=True)
    for badge in badges:
        UserBadge.objects.get_or_create(user=user, badge=badge)
    # Mastery badge
    if score == 100:
        mastery_badges = Badge.objects.filter(type='mastery', course_id=str(course_id), is_active=True)
        for badge in mastery_badges:
            UserBadge.objects.get_or_create(user=user, badge=badge)

def award_badges_for_streak(user, streak_days):
    badges = Badge.objects.filter(type='streak', streak_days__lte=streak_days, is_active=True)
    for badge in badges:
        UserBadge.objects.get_or_create(user=user, badge=badge)
