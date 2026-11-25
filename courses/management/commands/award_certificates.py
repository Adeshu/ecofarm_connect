from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Course, Certificate, CourseEnrollment

User = get_user_model()

class Command(BaseCommand):
    help = 'Award certificates to users who have completed courses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--course-id',
            type=int,
            help='Award certificates for specific course ID only',
        )
        parser.add_argument(
            '--user-id',
            help='Award certificate to specific user ID only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        # Filter courses
        courses = Course.objects.all()
        if options['course_id']:
            courses = courses.filter(id=options['course_id'])

        # Filter users
        users = User.objects.all()
        if options['user_id']:
            users = users.filter(id=options['user_id'])

        awarded_count = 0

        for course in courses:
            # Get completed enrollments for this course
            # Adjust this query based on your enrollment model structure
            completed_enrollments = CourseEnrollment.objects.filter(
                course=course,
                progress=100  # Assuming 100% means completed
            ).select_related('user')

            if options['user_id']:
                completed_enrollments = completed_enrollments.filter(
                    user_id=options['user_id']
                )

            for enrollment in completed_enrollments:
                if options['dry_run']:
                    exists = Certificate.objects.filter(
                        user=enrollment.user,
                        course=course
                    ).exists()
                    if not exists:
                        self.stdout.write(
                            f"Would award certificate: {enrollment.user.get_full_name()} - {course.title}"
                        )
                        awarded_count += 1
                else:
                    certificate, created = Certificate.objects.get_or_create(
                        user=enrollment.user,
                        course=course,
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Awarded certificate: {enrollment.user.get_full_name()} - {course.title}"
                            )
                        )
                        awarded_count += 1
                    else:
                        self.stdout.write(
                            f"Certificate already exists: {enrollment.user.get_full_name()} - {course.title}"
                        )

        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f"Dry run complete. Would award {awarded_count} certificates.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully awarded {awarded_count} new certificates.")
            )
