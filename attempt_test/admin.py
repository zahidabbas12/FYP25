from django.contrib import admin
from .models import TestAttempt, QuestionAttempt

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'attempt_date', 'score', 'percentage', 'is_completed')
    list_filter = ('is_completed', 'attempt_date', 'test')
    search_fields = ('user__username', 'test__title')
    date_hierarchy = 'attempt_date'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'test', 'attempt_date')
        }),
        ('Results', {
            'fields': ('score', 'percentage', 'is_completed', 'start_time')
        }),
    )

@admin.register(QuestionAttempt)
class QuestionAttemptAdmin(admin.ModelAdmin):
    list_display = ('test_attempt', 'question', 'selected_option', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('test_attempt__user__username', 'question__question')
    raw_id_fields = ('test_attempt', 'question')
