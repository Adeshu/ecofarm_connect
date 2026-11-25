from django.contrib import admin
from django.utils.html import format_html
from .models import CourseCategory, Course, Lesson, CourseEnrollment, Certificate

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'courses_count', 'color_display', 'created_at')
    search_fields = ('name', 'description')

    def courses_count(self, obj):
        return obj.courses.count()
    courses_count.short_description = 'Courses Count'

    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'lesson_type', 'order', 'duration_minutes', 'is_free')
    ordering = ('order',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'status', 'points_reward', 'created_at', 'completion_count')
    list_filter = ('category', 'difficulty', 'status', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('prerequisites',)
    inlines = [LessonInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'category')
        }),
        ('Course Details', {
            'fields': ('difficulty', 'duration_hours', 'points_reward', 'thumbnail')
        }),
        ('Content', {
            'fields': ('content', 'status')
        }),
        ('Prerequisites', {
            'fields': ('prerequisites',)
        })
    )

    def completion_count(self, obj):
        return obj.completion_count()
    completion_count.short_description = 'Completions'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'lesson_type', 'order', 'duration_minutes', 'is_free')
    list_filter = ('lesson_type', 'is_free', 'course__category')
    search_fields = ('title', 'course__title')
    ordering = ('order',)

    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'lesson_type', 'order', 'duration_minutes', 'is_free')
        }),
        ('Content', {
            'fields': ('content', 'video_url', 'video_file', 'assignment_file', 'quiz_questions', 'practical_instructions'),
            'classes': ('collapse',),
        }),
    )

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress', 'enrolled_at', 'completed_at', 'certificate_issued')
    list_filter = ('enrolled_at', 'completed_at', 'certificate_issued', 'course__category')
    search_fields = ('user__phone', 'user__first_name', 'course__title')
    readonly_fields = ('enrolled_at',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'certificate_code', 'verification_code', 'issued_at')
    list_filter = ('issued_at', 'course__category')
    search_fields = ('user__phone', 'user__first_name', 'course__title', 'certificate_code', 'verification_code')
    readonly_fields = ('certificate_code', 'verification_code', 'issued_at')
