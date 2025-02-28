#performance_analytics/models.py
from django.conf import settings
from django.db import models
from attempt_test.models import TestAttempt
from django.contrib.auth import get_user_model

class PerformanceAnalytics(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='analytics')
    score = models.IntegerField()
    percentage = models.FloatField()
    attempt_date = models.DateTimeField()

    def __str__(self):
        return f"{self.student.username} - {self.test.test.name} Performance"

class Feedback(models.Model):
    teacher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='feedback_given')
    test_attempt = models.OneToOneField(TestAttempt, on_delete=models.CASCADE, related_name='feedback')
    content = models.TextField()

    def __str__(self):
        return f"Feedback for {self.test_attempt.test.name} by {self.teacher.username}"