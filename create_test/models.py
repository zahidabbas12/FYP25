from django.db import models
from accounts.models import CustomUser
from question_bank.models import MCQ

class Test(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    pass_mark = models.PositiveIntegerField(help_text="Pass percentage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Tests'

class TestMCQ(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_mcqs')
    mcq = models.ForeignKey(MCQ, on_delete=models.CASCADE)
    order = models.PositiveBigIntegerField()

    class Meta:
        ordering = ['order']
    def __str__(self):
        return f"Q{self.order}: {self.mcq.question_text} in {self.test.title}"
    
    class Meta:
        verbose_name = 'Test question'
        verbose_name_plural = 'Test questions'