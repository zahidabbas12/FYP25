from django.urls import path 
from . import views

urlpatterns = [
    path('create/', views.create_test, name='create_test'),
    path('list/', views.manage_tests, name='manage_tests'),
    path('<int:test_id>/add-mcqs/', views.add_mcqs_to_test, name='add_mcqs_to_test'),
    path('tests/edit/<int:test_id>/', views.edit_test, name='edit_test'),
    path('tests/delete/<int:test_id>/', views.delete_test, name='delete_test'),

]
