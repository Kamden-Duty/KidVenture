from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', views.login_view, name = 'login_view'),
    path('register/', views.register, name = 'register'),
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

    
]