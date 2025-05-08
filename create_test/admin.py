from django.contrib import admin
from .models import Test, TestMCQ

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'duration', 'pass_mark', 'is_published', 'is_active', 'created_at')
    list_filter = ('is_published', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'teacher__username')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('teacher', 'title', 'description')
        }),
        ('Test Settings', {
            'fields': ('duration', 'pass_mark', 'is_published', 'is_active')
        }),
    )

@admin.register(TestMCQ)
class TestMCQAdmin(admin.ModelAdmin):
    list_display = ('test', 'mcq', 'order')
    list_filter = ('test',)
    search_fields = ('test__title', 'mcq__question')
    ordering = ('test', 'order')
