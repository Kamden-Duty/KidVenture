from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import get_last_session
from django.contrib.auth import views as auth_views 
from .forms import LoginForm
from .views import ResetPasswordView  
from .views import (
    ResetPasswordView,
    CustomPasswordResetConfirmView,   
)

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('home', views.home, name='home'),
    path('logout/', views.logout_view, name='logout_view'),
    path('create_class/', views.create_class, name='create_class'),
    path('student/', views.student_homepage, name='student_homepage'),
    path('student/home/', views.student_homepage, name='student_home'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('profile/', views.view_profile, name='view_profile'),

    path('teacher_page/', views.home, name='teacher'),
    path('alphabet_matching/', views.alphabet_matching, name='alphabet_matching'),
    path('alphabet_memory/', views.alphabet_memory, name='alphabet_memory'),
    # path('game_selection/', views.game_selection, name='game_selection'),
    path('classes', views.classes, name='classes'),
    path('delete-class/<int:class_id>/', views.delete_class, name='delete_class'),
    path('join-class/', views.join_class, name='join_class'),
    path('students/', views.teacher_students, name='teacher_students'),
    path('delete-student/<int:student_id>/<int:class_id>/', views.delete_student, name='delete_student'),
    path('save_game_progress/', views.save_game_progress, name='save_game_progress'),    path('assign_activity/', views.assign_activity, name='assign_activity'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('teacher-leaderboard/', views.get_teacher_leaderboard, name='get_teacher_leaderboard'),
    path("edit-avatar/", views.edit_avatar, name="edit_avatar"),
    path("update-avatar-preview/", views.update_avatar_preview, name="update_avatar_preview"),


    path('get_last_session/', get_last_session, name='get_last_session'),
    path('check_activity_progress/<int:activity_id>/', views.check_activity_progress, name='check_activity_progress'),
    path('get_activity_progress/<int:activity_id>/', views.get_activity_progress, name='get_activity_progress'),
    path('complete_activity/<int:activity_id>/', views.complete_activity, name='complete_activity'),
    path('reset_free_play_progress/', views.reset_free_play_progress, name='reset_free_play_progress'),
    path('delete_activity/<int:activity_id>/', views.delete_activity, name='delete_activity'),
    path('complete_class_activitsy/<int:activity_id>/', views.complete_class_activity, name='complete_class_activity'),
    path('progress-overview/', views.progress_overview, name='progress_overview'),
    path('get_class_total_progress/<int:class_id>/', views.get_class_total_progress, name='get_class_total_progress'),
    path("get_class_activities/<int:class_id>/", views.get_class_activities, name="get_class_activities"),


    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'), 

    
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        CustomPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),


    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='KidVenture/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    
    path(
      'login/',
      auth_views.LoginView.as_view(
        template_name='KidVenture/login.html',
        authentication_form=LoginForm
      ),
      name='login'
    ),    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)