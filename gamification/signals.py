from django.db.models.signals import post_save
from django.dispatch import receiver
from quests.models import QuestCompletion
from courses.models import CourseEnrollment
from .services import award_badges_for_quest_completion, award_badges_for_course_completion, award_badges_for_streak

@receiver(post_save, sender=QuestCompletion)
def handle_quest_badge(sender, instance, created, **kwargs):
    if created and instance.is_completed:
        award_badges_for_quest_completion(instance.user, instance.quest.id)

@receiver(post_save, sender=CourseEnrollment)
def handle_course_badge(sender, instance, created, **kwargs):
    if instance.progress == 100:
        award_badges_for_course_completion(instance.user, instance.course.id, getattr(instance, 'score', None))
