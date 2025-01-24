from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import register, login_view, redirect_dashboard, teacher_dashboard, student_dashboard, logout_view

urlpatterns = [
    
    path('', views.home, name='home'),
    path('redirect_dashboard/', views.redirect_dashboard, name='redirect_dashboard'), 
    path('register/', register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile_view'),  
    path('edit_profile/', views.profile_edit, name='profile_edit'), 
    path('delete_profile/', views.profile_delete, name='profile_delete'),
    path('teacher_dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('student_dashboard/', student_dashboard, name='student_dashboard'),
]