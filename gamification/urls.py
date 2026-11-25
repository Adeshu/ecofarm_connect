from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('badges/', views.badges, name='badges'),
    path('my-badges/', views.my_badges, name='my_badges'),
    path('my-achievements/', views.my_achievements, name='my_achievements'),
    path('points-history/', views.points_history, name='points_history'),
    path('profile/<uuid:user_id>/', views.user_profile_public, name='user_profile_public'),
]
