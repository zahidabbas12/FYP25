from django.urls import path
from . import views

app_name = 'attempt_test'

urlpatterns = [
    path('tests/', views.view_tests, name='view_tests'),
    path('test/<int:test_id>/<int:question_index>/', views.attempt_test, name='attempt_test'),
    path('result/<int:test_attempt_id>/', views.test_result, name='result'),
    path('view_tests/', views.view_tests, name='view_tests'),
]
