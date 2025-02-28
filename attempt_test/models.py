# attempt_test/models.py
from django.conf import settings  # To access the custom user model if defined
from django.db import models
from question_bank.models import MCQ  # Assuming you have an MCQ model in your question_bank app
from create_test.models import Test  # Assuming the Test model is in your create_test app
from django.utils import timezone

class TestAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    attempt_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)  # Ensure the percentage field exists
    is_completed = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username} - {self.test.name}"
    

class QuestionAttempt(models.Model):
    test_attempt = models.ForeignKey(TestAttempt, related_name='question_attempts', on_delete=models.CASCADE)
    question = models.ForeignKey(MCQ, on_delete=models.CASCADE)  # Assuming MCQ questions
    selected_option = models.CharField(max_length=1)  # 'A', 'B', 'C', 'D'
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Question {self.question.id} - Attempt by {self.test_attempt.user.username}"
