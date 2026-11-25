import contextlib
import json
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, Http404
from django.utils import timezone
from django.utils.timezone import localtime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor

from .models import (
    CourseCategory,
    Course,
    Lesson,
    CourseEnrollment,
    Certificate,
    LessonProgress,
)
from accounts.models import User
from gamification.models import Achievement, PointsHistory


def course_list(request):
    """List all published courses with filtering and pagination"""
    courses = Course.objects.filter(status='published').select_related('category')
    categories = CourseCategory.objects.all()

    # Filters
    category_id = request.GET.get('category')
    if category_id:
        courses = courses.filter(category_id=category_id)

    difficulty = request.GET.get('difficulty')
    if difficulty:
        courses = courses.filter(difficulty=difficulty)

    search = request.GET.get('search')
    if search:
        courses = courses.filter(Q(title__icontains=search) | Q(description__icontains=search))

    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_difficulty': difficulty,
        'search_query': search,
        'difficulty_choices': Course.DIFFICULTY_CHOICES,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    """Course detail, lessons, enrollment, progress and certificate"""
    course = get_object_or_404(Course, slug=slug, status='published')
    lessons = course.lessons.all().order_by('order')
    is_enrolled = False
    enrollment = None
    progress = 0
    certificate = None
    completed_lesson_ids = set()
    total_enrollments = course.enrollments.count()

    if request.user.is_authenticated:
        with contextlib.suppress(CourseEnrollment.DoesNotExist):
            enrollment = CourseEnrollment.objects.get(user=request.user, course=course)
            is_enrolled = True
            progress = enrollment.progress
            completed_lesson_ids = set(
                LessonProgress.objects.filter(enrollment=enrollment, completed=True).values_list('lesson_id', flat=True)
            )
            if enrollment.certificate_issued:
                certificate = Certificate.objects.filter(user=request.user, course=course).first()

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'progress': progress,
        'completed_lesson_ids': completed_lesson_ids,
        'certificate': certificate,
        'total_enrollments': total_enrollments,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def lesson_detail(request, lesson_id):
    """Lesson detail with quiz support and progress tracking"""
    lesson = get_object_or_404(Lesson, id=lesson_id)

    # Enrollment check & lesson progress
    is_enrolled = False
    enrollment = None
    lesson_progress = None
    try:
        enrollment = CourseEnrollment.objects.get(user=request.user, course=lesson.course)
        is_enrolled = True
        lesson_progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    except CourseEnrollment.DoesNotExist:
        if not lesson.is_free:
            messages.error(request, 'You must be enrolled to access this lesson.')
            return redirect('courses:course_detail', slug=lesson.course.slug)

    # Get all lessons for the course (to show in sidebar)
    all_lessons = lesson.course.lessons.all().order_by('order')
    
    # Extract YouTube video ID
    youtube_id = None
    if lesson.video_url:
        if 'watch?v=' in lesson.video_url:
            youtube_id = lesson.video_url.split('watch?v=')[-1].split('&')[0]
        elif 'youtu.be/' in lesson.video_url:
            youtube_id = lesson.video_url.split('youtu.be/')[-1].split('?')[0]
    
    # Load quiz questions safely
    quiz = []
    if lesson.quiz_questions:
        try:
            quiz = json.loads(lesson.quiz_questions) if isinstance(lesson.quiz_questions, str) else lesson.quiz_questions
        except (json.JSONDecodeError, TypeError):
            quiz = []

    # Handle quiz submission
    submitted = False
    results = []
    user_answers = {}
    score = 0

    if request.method == 'POST' and quiz:
        submitted = True
        for i, question in enumerate(quiz):
            question_id = f"question_{i}"
            selected = request.POST.get(question_id)
            user_answers[question_id] = selected

            correct_answer = str(question.get('correct_answer', ''))
            is_correct = selected == correct_answer
            if is_correct:
                score += 1
            
            results.append({
                'question': question.get('question', ''),
                'options': question.get('options', []),
                'selected': selected,
                'correct': correct_answer,
                'is_correct': is_correct,
            })

    # Navigation lessons
    next_lesson = lesson.get_next_lesson()
    previous_lesson = lesson.get_previous_lesson()

    # Completed lessons
    completed_lessons = []
    if enrollment:
        completed_lessons = list(
            LessonProgress.objects.filter(enrollment=enrollment, completed=True).values_list('lesson_id', flat=True)
        )

    context = {
        'lesson': lesson,
        'youtube_id': youtube_id,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
        'is_enrolled': is_enrolled,
        'next_lesson': next_lesson,
        'previous_lesson': previous_lesson,
        'all_lessons': all_lessons,              
        'completed_lessons': completed_lessons,
        'quiz': quiz,
        'submitted': submitted,
        'results': results,
        'user_answers': user_answers,
        'score': score,
        'total_questions': len(quiz),
        'quiz_percentage': (score / len(quiz)) * 100 if len(quiz) > 0 else 0,
    }
    return render(request, 'courses/lesson_detail.html', context)


@login_required
def mark_lesson_complete(request, lesson_id):
    """Mark lesson complete and update progress"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    lesson = get_object_or_404(Lesson, id=lesson_id)
    try:
        enrollment = CourseEnrollment.objects.get(user=request.user, course=lesson.course)
    except CourseEnrollment.DoesNotExist:
        return JsonResponse({'error': 'Not enrolled in course'}, status=400)

    lesson_progress, created = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)

    if not lesson_progress.completed:
        lesson_progress.completed = True
        lesson_progress.completed_at = timezone.now()
        lesson_progress.save()

        enrollment.update_progress()

        points_awarded = 10
        request.user.total_points += points_awarded
        request.user.update_level()
        request.user.save()

        Achievement.objects.create(
            user=request.user,
            title=f'Lesson Completed: {lesson.title}',
            description=f'Completed lesson "{lesson.title}" in {lesson.course.title}',
            points_earned=points_awarded,
            related_object_id=str(lesson.id),
            related_object_type='lesson'
        )

        PointsHistory.objects.create(
            user=request.user,
            points_change=points_awarded,
            point_type='lesson_completion',
            description=f'Completed lesson: {lesson.title}',
            related_object_id=str(lesson.id),
            related_object_type='lesson'
        )

        if enrollment.progress == 100 and not enrollment.certificate_issued:
            enrollment.completed_at = timezone.now()
            enrollment.certificate_issued = True
            enrollment.save()

            Certificate.objects.create(user=request.user, course=lesson.course)

            return JsonResponse({
                'success': True,
                'message': 'Lesson completed! Course finished - Certificate issued!',
                'course_completed': True,
                'progress': enrollment.progress,
            })

    return JsonResponse({
        'success': True,
        'message': 'Lesson marked as complete!',
        'progress': enrollment.progress,
    })


@login_required
def enroll_course(request, course_id):
    """Enroll user in course"""
    course = get_object_or_404(Course, id=course_id, status='published')

    if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course!')
        return redirect('courses:course_detail', slug=course.slug)

    CourseEnrollment.objects.create(user=request.user, course=course)
    request.user.total_points += 10
    request.user.update_level()
    request.user.save()

    Achievement.objects.create(
        user=request.user,
        title=f'Enrolled in {course.title}',
        description=f'Started learning {course.title}',
        points_earned=10,
        related_object_id=str(course.id),
        related_object_type='course',
    )

    PointsHistory.objects.create(
        user=request.user,
        points_change=10,
        point_type='course_enrollment',
        description=f'Enrolled in course: {course.title}',
        related_object_id=str(course.id),
        related_object_type='course',
    )

    messages.success(request, f'Successfully enrolled in {course.title}! You earned 10 points!')
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def complete_course(request, course_id):
    """Mark course as completed manually"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    course = get_object_or_404(Course, id=course_id, status='published')
    try:
        enrollment = CourseEnrollment.objects.get(user=request.user, course=course)
    except CourseEnrollment.DoesNotExist:
        return JsonResponse({'error': 'Not enrolled'}, status=400)

    if enrollment.progress < 100:
        enrollment.progress = 100
        enrollment.completed_at = timezone.now()
        enrollment.certificate_issued = True
        enrollment.save()

        request.user.total_points += course.points_reward
        request.user.update_level()
        request.user.save()

        Achievement.objects.create(
            user=request.user,
            title=f'Course Completed: {course.title}',
            description=f'Successfully completed {course.title}',
            points_earned=course.points_reward,
            related_object_id=str(course.id),
            related_object_type='course',
        )

        PointsHistory.objects.create(
            user=request.user,
            points_change=course.points_reward,
            point_type='course_completion',
            description=f'Completed course: {course.title}',
            related_object_id=str(course.id),
            related_object_type='course',
        )

        Certificate.objects.create(user=request.user, course=course)

        try:
            from gamification.models import Badge, UserBadge
            badges = Badge.objects.filter(
                points_required__lte=request.user.total_points,
                is_active=True,
            ).exclude(user_badges__user=request.user)

            new_badges = []
            for badge in badges:
                user_badge, created = UserBadge.objects.get_or_create(user=request.user, badge=badge)
                if created:
                    new_badges.append(badge.name)

            response_data = {
                'success': True,
                'points_earned': course.points_reward,
                'total_points': request.user.total_points,
                'level': request.user.level,
                'message': f'Congratulations! You earned {course.points_reward} points!',
            }

            if new_badges:
                response_data['new_badges'] = new_badges
                response_data['message'] += f' New badges earned: {", ".join(new_badges)}'

            return JsonResponse(response_data)
        except ImportError:
            pass

    return JsonResponse({'success': True, 'message': 'Course already completed'})


@login_required
def my_courses(request):
    """Show user's enrolled courses filtered by status"""
    enrollments = CourseEnrollment.objects.filter(user=request.user).select_related('course')

    status_filter = request.GET.get('status')
    if status_filter == 'completed':
        enrollments = enrollments.filter(progress=100)
    elif status_filter == 'in_progress':
        enrollments = enrollments.filter(progress__gt=0, progress__lt=100)
    elif status_filter == 'not_started':
        enrollments = enrollments.filter(progress=0)

    context = {
        'enrollments': enrollments,
        'current_status': status_filter,
    }
    return render(request, 'courses/my_courses.html', context)


@login_required
def certificate_pdf(request, cert_id):
    """Generate a modern styled PDF certificate"""
    cert = get_object_or_404(Certificate.objects.select_related('user', 'course'), id=cert_id)

    # Authorization check
    if cert.user_id != request.user.id and not request.user.is_staff:
        raise Http404("Certificate not found")

    response = HttpResponse(content_type='application/pdf')
    filename = f"{cert.user.first_name}_{cert.course.title}_Certificate.pdf".replace(' ', '_')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Colors
    primary_green = HexColor('#28a745')
    dark_green = HexColor('#1e7e34')
    light_gray = HexColor('#f8f9fa')

    # Modern border design
    p.setStrokeColor(primary_green)
    p.setLineWidth(8)
    p.rect(40, 40, width-80, height-80, fill=0)

    # Inner border
    p.setStrokeColor(dark_green)
    p.setLineWidth(2)
    p.rect(60, 60, width-120, height-120, fill=0)

    # Header background
    p.setFillColor(light_gray)
    p.rect(80, height-180, width-160, 100, fill=1, stroke=0)

    # Title
    p.setFillColor(primary_green)
    p.setFont("Helvetica-Bold", 36)
    p.drawCentredString(width/2, height-120, "CERTIFICATE")
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, height-150, "OF COMPLETION")

    # Decorative line
    p.setStrokeColor(primary_green)
    p.setLineWidth(3)
    p.line(100, height-200, width-100, height-200)

    # Certification text
    p.setFillColor(HexColor('#333333'))
    p.setFont("Helvetica", 18)
    p.drawCentredString(width/2, height-250, "This is to certify that")

    # User name
    p.setFillColor(primary_green)
    p.setFont("Helvetica-Bold", 32)
    p.drawCentredString(width/2, height-300, cert.user.get_full_name())

    # Course completed
    p.setFillColor(HexColor('#333333'))
    p.setFont("Helvetica", 16)
    p.drawCentredString(width/2, height-340, "has successfully completed the course")

    # Course title
    p.setFillColor(dark_green)
    p.setFont("Helvetica-Bold", 22)
    p.drawCentredString(width/2, height-380, cert.course.title)

    # Certificate info
    p.setFillColor(HexColor('#666666'))
    p.setFont("Helvetica-Oblique", 14)
    issued_date = cert.issued_at.strftime('%B %d, %Y')
    p.drawCentredString(width/2, height-440, f"Issued on: {issued_date}")
    p.drawCentredString(width/2, height-460, f"Certificate ID: {cert.certificate_code}")
    p.drawCentredString(width/2, height-480, f"Verification Code: {cert.verification_code}")

    # Footer branding
    p.setFillColor(primary_green)
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, 120, "EcoFarm Connect")
    p.setFont("Helvetica", 12)
    p.drawCentredString(width/2, 100, "Sustainable Farming Education Platform")

    # Verification URL
    p.setFillColor(HexColor('#666666'))
    p.setFont("Helvetica", 10)
    verify_url = f"https://ecofarmconnect.com/courses/verify/{cert.id}"
    p.drawCentredString(width/2, 80, f"Verify at: {verify_url}")

    p.showPage()
    p.save()
    return response


def certificate_verify(request, cert_id):
    """Public certificate verification page"""
    try:
        cert = get_object_or_404(Certificate.objects.select_related('user', 'course'), id=cert_id)
        context = {
            'cert': cert,
            'user': cert.user,
            'course': cert.course,
            'issued_date': localtime(cert.issued_at),
            'certificate_id': cert.certificate_code,
            'verification_code': cert.verification_code,
            'site_name': 'EcoFarm Connect',
            'verified': True,
        }
        return render(request, 'courses/certificate_verify.html', context)
    except Certificate.DoesNotExist:
        return render(request, 'courses/certificate_verify.html', {
            'verified': False,
            'error_message': 'Certificate not found or invalid.',
            'site_name': 'EcoFarm Connect',
        })


@login_required
def my_certificates(request):
    """Show user's certificates with pagination"""
    certificates = Certificate.objects.filter(user=request.user).select_related('course').order_by('-issued_at')

    paginator = Paginator(certificates, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'courses/my_certificates.html', {
        'certificates': page_obj,
        'total_certificates': certificates.count(),
    })
