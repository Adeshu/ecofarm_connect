from django.urls import path
from . import views

app_name = 'quests'

urlpatterns = [
    path('', views.quest_list, name='quest_list'),
    path('my-quests/', views.my_quests, name='my_quests'),
    path('<uuid:quest_id>/', views.quest_detail, name='quest_detail'),
    path('complete/<uuid:quest_id>/', views.complete_quest, name='complete_quest'),
    path('<uuid:quest_id>/step/<int:step_id>/complete/', views.complete_quest_step, name='complete_quest_step'),
]
