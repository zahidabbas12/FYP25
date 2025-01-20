# question_bank/admin.py
from django.contrib import admin
from .models import MCQ

# Registering the MCQ model
@admin.register(MCQ)
class MCQAdmin(admin.ModelAdmin):
    list_display = ('question', 'teacher', 'difficulty', 'category', 'correct_answer')
    search_fields = ('question', 'category', 'teacher__username')
    list_filter = ('difficulty', 'category')

    # Optional: Add additional fields for editing
    fieldsets = (
        (None, {
            'fields': ('teacher', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation', 'difficulty', 'category')
        }),
    )

  
