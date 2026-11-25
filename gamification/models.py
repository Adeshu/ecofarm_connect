from django.db import models
from django.conf import settings
import uuid

from django.db import models
from django.conf import settings
import uuid

class Badge(models.Model):
    # Add badge types for dynamic assignment
    BADGE_TYPE_CHOICES = [
        ('milestone', 'Milestone'),
        ('expertise', 'Expertise'),
        ('achievement', 'Achievement'),
        ('special', 'Special'),
        ('seasonal', 'Seasonal'),
        ('quest', 'Quest Completion'),
        ('course', 'Course Completion'),
        ('mastery', 'Course Mastery'),
        ('streak', 'Streak'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-award')
    color = models.CharField(max_length=7, default='#ffc107')
    points_required = models.PositiveIntegerField(help_text='Points needed to earn this badge')
    category = models.CharField(max_length=20, choices=BADGE_TYPE_CHOICES, default='milestone')
    type = models.CharField(max_length=20, choices=BADGE_TYPE_CHOICES, default='milestone')
    quest_id = models.CharField(max_length=100, blank=True, null=True, help_text='Awarded for quest id (if quest badge)')
    course_id = models.CharField(max_length=100, blank=True, null=True, help_text='Awarded for course id (if course/mastery badge)')
    streak_days = models.PositiveIntegerField(blank=True, null=True, help_text='Awarded for minimum streak days (if streak badge)')
    is_active = models.BooleanField(default=True)
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ], default='common')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['points_required', 'name']

    def __str__(self):
        return self.name

    @property
    def earned_count(self):
        return self.user_badges.count()


class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user} earned {self.badge.name}"

class Achievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    description = models.TextField()
    points_earned = models.PositiveIntegerField(default=0)
    achieved_at = models.DateTimeField(auto_now_add=True)
    related_object_id = models.CharField(max_length=100, blank=True, help_text='ID of related object (quest, course, etc.)')
    related_object_type = models.CharField(max_length=50, blank=True, help_text='Type of related object')

    class Meta:
        ordering = ['-achieved_at']

    def __str__(self):
        return f"{self.user} - {self.title}"

class PointsHistory(models.Model):
    POINT_TYPES = [
        ('quest_completion', 'Quest Completion'),
        ('course_completion', 'Course Completion'),
        ('farm_activity', 'Farm Activity'),
        ('badge_earned', 'Badge Earned'),
        ('daily_login', 'Daily Login'),
        ('community_help', 'Community Help'),
        ('bonus', 'Bonus Points'),
        ('penalty', 'Points Penalty'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='points_history')
    points_change = models.IntegerField(help_text='Positive for earned, negative for lost')
    point_type = models.CharField(max_length=30, choices=POINT_TYPES)
    description = models.CharField(max_length=300)
    related_object_id = models.CharField(max_length=100, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.points_change > 0 else ''
        return f"{self.user}: {sign}{self.points_change} pts - {self.description}"

class Leaderboard(models.Model):
    LEADERBOARD_TYPES = [
        ('overall', 'Overall Points'),
        ('monthly', 'Monthly Points'),
        ('quests', 'Quest Completions'),
        ('courses', 'Course Completions'),
        ('farms', 'Farm Activities'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    leaderboard_type = models.CharField(max_length=20, choices=LEADERBOARD_TYPES)
    score = models.PositiveIntegerField()
    rank = models.PositiveIntegerField()
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'leaderboard_type', 'period_start']
        ordering = ['rank']

    def __str__(self):
        return f"{self.user} - Rank #{self.rank} in {self.get_leaderboard_type_display()}"
