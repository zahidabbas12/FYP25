from django.urls import path
from . import views

urlpatterns = [
    path('manage/', views.manage_questions, name='manage_questions'),
    path('add/', views.add_question, name='add_question'),
    path('<int:id>/edit/', views.edit_question, name='edit_question'), 
    path('<int:id>/delete/', views.delete_question, name='delete_question'),
    path('<int:id>/update-category/', views.update_category, name='update_category'),
]