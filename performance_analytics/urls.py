# performance_analytics/urls.py
from django.urls import path
from . import views

app_name = 'performance_analytics'

urlpatterns = [
    # Student URLs
    path('user_performance/<int:user_id>/', views.user_performance, name='user_performance'),
    path('visualize_performance/<int:user_id>/', views.visualize_performance, name='visualize_performance'),
    
    # Teacher URLs
    path('student_performance/<int:user_id>/', views.student_performance, name='student_performance'),
    path('visualize_student_performance/<int:user_id>/', views.visualize_student_performance, name='visualize_student_performance'),
    
    # Other URLs
    path('test/<int:test_attempt_id>/', views.test_details, name='test_details'),
    path('test/<int:test_attempt_id>/feedback/create/', views.create_feedback, name='create_feedback'),
    path('test/<int:test_attempt_id>/feedback/update/', views.update_feedback, name='update_feedback'),
    path('test/<int:test_attempt_id>/feedback/delete/', views.delete_feedback, name='delete_feedback'),
    path('student/<int:student_id>/analytics/', views.student_analytics, name='student_analytics'),
]
