from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-book')
    color = models.CharField(max_length=7, default='#28a745', help_text='Hex color code')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Course Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField()
    content = models.TextField(help_text='Full course content in markdown or HTML')
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='courses')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_hours = models.PositiveIntegerField(help_text='Estimated duration in hours')
    points_reward = models.PositiveIntegerField(default=100, help_text='Points awarded upon completion')
    thumbnail = models.URLField(blank=True, help_text='Course thumbnail image URL')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    prerequisites = models.ManyToManyField('self', blank=True,)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def completion_count(self):
        return self.enrollments.filter(progress=100).count()

    completion_count.short_description = 'Completion Count'

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('practical', 'Practical Exercise'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='text')
    video_url = models.URLField(blank=True, help_text='YouTube or video URL')
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True, help_text='Upload video file (MP4, WebM, etc.)')
    assignment_file = models.FileField(upload_to='assignments/', blank=True, null=True)
    quiz_questions = models.JSONField(blank=True, null=True, help_text='Quiz questions in JSON format')
    practical_instructions = models.TextField(blank=True, help_text='Step-by-step practical instructions')
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=10)
    is_free = models.BooleanField(default=False, help_text='Free preview lesson')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = [('course', 'order')]

    def __str__(self):
        return f'{self.course.title} - {self.title}'

    def get_next_lesson(self):
        return Lesson.objects.filter(course=self.course, order__gt=self.order).order_by('order').first()

    def get_previous_lesson(self):
        return Lesson.objects.filter(course=self.course, order__lt=self.order).order_by('-order').first()


class CourseEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    certificate_issued = models.BooleanField(default=False)

    class Meta:
        ordering = ['-enrolled_at']
        unique_together = [('user', 'course')]

    def __str__(self):
        return f'{self.user.email} - {self.course.title}'

    def calculate_progress(self):
        """Calculate progress based on completed lessons"""
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        completed_lessons = LessonProgress.objects.filter(
            enrollment=self, completed=True
        ).count()
        return int((completed_lessons / total_lessons) * 100)

    def update_progress(self):
        """Update the progress field based on completed lessons"""
        self.progress = self.calculate_progress()
        self.save(update_fields=['progress'])


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(CourseEnrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('enrollment', 'lesson')]

    def __str__(self):
        return f'{self.enrollment.user.email} - {self.lesson.title} - {"Completed" if self.completed else "In Progress"}'


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    verification_code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['-issued_at']
        unique_together = [('user', 'course')]

    def __str__(self):
        return f'Certificate for {self.user.email} - {self.course.title}'

    def save(self, *args, **kwargs):
        if not self.certificate_code:
            self.certificate_code = f'CERT-{str(self.id)[:8].upper()}'
        if not self.verification_code:
            self.verification_code = f'VERIFY-{str(self.id)[:8].upper()}'
        super().save(*args, **kwargs)
