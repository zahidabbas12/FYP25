from django.contrib import admin
from .models import Test, TestMCQ
from question_bank.models import MCQ  # Assuming MCQs are in the 'question_bank' app

class TestMCQInline(admin.TabularInline):  # You can also use StackedInline for a different layout
    model = TestMCQ
    extra = 1  # How many empty rows to show by default
    fields = ('mcq', 'order')  # Fields to display in the inline form
    autocomplete_fields = ['mcq']  # If you want autocompletion for selecting MCQs

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'is_published', 'duration', 'pass_mark', 'get_mcqs')
    search_fields = ('title', 'teacher__username')  # Search by title or teacher's username
    inlines = [TestMCQInline]  # Add the inline to the Test admin

    def get_mcqs(self, obj):
        """
        Custom method to show related MCQs in the list view.
        Uses the correct reverse relation 'test_mcqs' from Test model.
        """
        return ", ".join([str(mcq.mcq.question) for mcq in obj.test_mcqs.all()])
    
    get_mcqs.short_description = 'MCQs'  # This is the column header
