from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class QuestCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-tasks')
    color = models.CharField(max_length=7, default='#28a745')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Quest Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Quest(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructions = models.TextField(help_text='Step-by-step instructions', default='')
    category = models.ForeignKey(QuestCategory, on_delete=models.CASCADE, related_name='quests', default=1)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    points_reward = models.PositiveIntegerField(default=50)
    time_limit_hours = models.PositiveIntegerField(default=24, help_text='Hours to complete')
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='unlocks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def completion_count(self):
        return self.completions.count()

    @property
    def completion_rate(self):
        """Calculate completion rate based on quest step completions for current user"""
        total_steps = self.steps.count()
        if total_steps == 0:
            return 0
        # This will be calculated per user in the view
        return 0


class QuestCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quest_completions')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='completions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    points_earned = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'quest']
        ordering = ['-completed_at']

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.user} - {self.quest.title} ({status})"


class QuestStep(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    points_value = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ['order']
        unique_together = ['quest', 'order']

    def __str__(self):
        return f"{self.quest.title} - Step {self.order}: {self.title}"


class QuestStepCompletion(models.Model):
    completion = models.ForeignKey(QuestCompletion, on_delete=models.CASCADE, related_name='step_completions')
    step = models.ForeignKey(QuestStep, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    evidence = models.FileField(upload_to='quest_evidence/', blank=True, null=True)

    class Meta:
        unique_together = ['completion', 'step']

    def __str__(self):
        return f"{self.completion.user} completed {self.step.title}"
