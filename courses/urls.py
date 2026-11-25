from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('my-certificates/', views.my_certificates, name='my_certificates'),
    path('enroll/<uuid:course_id>/', views.enroll_course, name='enroll_course'),
    path('complete/<uuid:course_id>/', views.complete_course, name='complete_course'),
    path('verify/<str:verification_code>/', views.certificate_verify, name='certificate_verify'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('certificates/<uuid:cert_id>/download/', views.certificate_pdf, name='certificate_pdf'),
    path('certificates/<uuid:cert_id>/verify/', views.certificate_verify, name='certificate_verify'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
]
