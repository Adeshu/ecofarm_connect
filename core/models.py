from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class SiteSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site_name = models.CharField(max_length=100, default="EcoFarm Connect")
    site_description = models.TextField(default="Gamified platform to promote sustainable farming practices")
    contact_email = models.EmailField(default="info@ecofarmconnect.com")
    registration_open = models.BooleanField(default=True)
    points_per_level = models.PositiveIntegerField(default=500)
    daily_login_points = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.site_name

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('quest_available', 'New Quest Available'),
        ('quest_completed', 'Quest Completed'),
        ('badge_earned', 'Badge Earned'),
        ('level_up', 'Level Up'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"

class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('quests', 'Quests'),
        ('gamification', 'Gamification'),
        ('farming', 'Farming Practices'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category.title()}: {self.question[:50]}..."
