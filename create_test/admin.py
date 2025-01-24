from django.contrib import admin
from .models import Test, TestMCQ
from question_bank.models import MCQ

class TestMCQInline(admin.TabularInline):
    model = TestMCQ
    extra = 1
    fields = ('mcq', 'order')
    autocomplete_fields = ['mcq']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'is_published', 'duration', 'pass_mark', 'get_mcqs')
    search_fields = ('title', 'teacher__username')
    inlines = [TestMCQInline]

    def get_mcqs(self, obj):
        return ", ".join([str(mcq.mcq.question) for mcq in obj.test_mcqs.all()])
    get_mcqs.short_description = 'MCQs'
