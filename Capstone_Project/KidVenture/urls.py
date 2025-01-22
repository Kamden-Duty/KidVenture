from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login/', views.login_view, name = 'login_view'),
    path('register/', views.register, name = 'register'),
    path('home', views.home, name='home'),
    path('logout/', views.logout_view, name='logout_view'),
    path('create_class/', views.create_class, name='create_class'),
    # path('student_page/', views.home, name='student'),
    # path('teacher_page/', views.home, name='teacher'),
    
]