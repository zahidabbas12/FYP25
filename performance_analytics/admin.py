from django.contrib import admin
from .models import PerformanceAnalytics, Feedback

@admin.register(PerformanceAnalytics)
class PerformanceAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'score', 'percentage', 'attempt_date')
    list_filter = ('attempt_date',)
    search_fields = ('student__username', 'test__test__title')
    date_hierarchy = 'attempt_date'
    
    fieldsets = (
        (None, {
            'fields': ('student', 'test', 'attempt_date')
        }),
        ('Performance Metrics', {
            'fields': ('score', 'percentage')
        }),
    )

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'test_attempt', 'sentiment_label', 'sentiment_score')
    list_filter = ('sentiment_label',)
    search_fields = ('teacher__username', 'test_attempt__test__title', 'content')
    raw_id_fields = ('teacher', 'test_attempt')
    
    fieldsets = (
        (None, {
            'fields': ('teacher', 'test_attempt', 'content')
        }),
        ('Sentiment Analysis', {
            'fields': ('sentiment_score', 'sentiment_label'),
            'classes': ('collapse',)
        }),
    )
