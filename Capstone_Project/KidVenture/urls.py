from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', views.login_view, name = 'login_view'),
    path('register/', views.register, name = 'register'),
    path('home', views.home, name='home'),
    path('logout/', views.logout_view, name='logout_view'),
    path('create_class/', views.create_class, name='create_class'),
    path('classes', views.classes, name='classes'),
    path('delete-class/<int:class_id>/', views.delete_class, name='delete_class'),
    path('join-class/', views.join_class, name='join_class'),
    path('students/', views.teacher_students, name='teacher_students'),
    path('delete-student/<int:student_id>/<int:class_id>/', views.delete_student, name='delete_student'),

   # path('add-student/<int:class_id>/', views.add_student, name='add_student'),
    # path('student_page/', views.home, name='student'),
    # path('teacher_page/', views.home, name='teacher'),
    
]