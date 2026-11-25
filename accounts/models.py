# accounts/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)  # new identifier
    phone = models.CharField(max_length=17, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    total_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    class Meta:
        db_table = 'accounts_user'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def current_level(self):
        if self.total_points < 100:
            return 1
        elif self.total_points < 300:
            return 2
        elif self.total_points < 600:
            return 3
        elif self.total_points < 1000:
            return 4
        else:
            return 5

    def update_level(self):
        new_level = self.current_level
        if self.level != new_level:
            self.level = new_level
            self.save(update_fields=['level'])

    def get_leaderboard_position(self):
        users_with_more_points = User.objects.filter(total_points__gt=self.total_points).count()
        return users_with_more_points + 1
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date

User = get_user_model()

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer Not to Say'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    preferred_farming_type = models.CharField(max_length=100, blank=True)
    farming_experience_years = models.PositiveIntegerField(default=0)
    phone = models.CharField(max_length=17, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    village = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
