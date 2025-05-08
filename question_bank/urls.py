from django.urls import path
from . import views

urlpatterns = [
    path('manage/', views.manage_questions, name='manage_questions'),
    path('add/', views.add_question, name='add_question'),
    path('<int:id>/edit/', views.edit_question, name='edit_question'), 
    path('delete-question/<int:id>/', views.delete_question, name='delete_question'),
    path('<int:id>/update-category/', views.update_category, name='update_category'),
    path('generate_mcqs/', views.generate_mcqs, name='generate_mcqs'),
    path('save_mcqs/', views.save_mcqs, name='save_mcqs'),
    path('delete_generated_mcqs/', views.delete_generated_mcqs, name='delete_generated_mcqs'),
    path('delete-selected-questions/', views.delete_selected_questions, name='delete_selected_questions'),
]