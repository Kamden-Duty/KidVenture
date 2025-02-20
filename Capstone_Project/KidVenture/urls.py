from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import get_last_session

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('home', views.home, name='home'),
    path('logout/', views.logout_view, name='logout_view'),
    path('create_class/', views.create_class, name='create_class'),
    path('student/', views.student_homepage, name='student_homepage'),
    path('teacher_page/', views.home, name='teacher'),
    path('alphabet_matching/', views.alphabet_matching, name='alphabet_matching'),
    path('alphabet_memory/', views.alphabet_memory, name='alphabet_memory'),
    path('game_selection/', views.game_selection, name='game_selection'),
    path('classes', views.classes, name='classes'),
    path('delete-class/<int:class_id>/', views.delete_class, name='delete_class'),
    path('join-class/', views.join_class, name='join_class'),
    path('students/', views.teacher_students, name='teacher_students'),
    path('delete-student/<int:student_id>/<int:class_id>/', views.delete_student, name='delete_student'),
    path('save_game_progress/', views.save_game_progress, name='save_game_progress'),    path('assign_activity/', views.assign_activity, name='assign_activity'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path("edit-avatar/", views.edit_avatar, name="edit_avatar"),
     path("update-avatar-preview/", views.update_avatar_preview, name="update_avatar_preview"),


    path('get_last_session/', get_last_session, name='get_last_session'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)