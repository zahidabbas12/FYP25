#performance_analytics/models.py
from django.conf import settings
from django.db import models
from attempt_test.models import TestAttempt
from django.contrib.auth import get_user_model
from textblob import TextBlob

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
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_label = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Analyze sentiment before saving
        if self.content:
            blob = TextBlob(self.content)
            self.sentiment_score = blob.sentiment.polarity
            
            # Determine sentiment label
            if self.sentiment_score > 0.1:
                self.sentiment_label = 'positive'
            elif self.sentiment_score < -0.1:
                self.sentiment_label = 'negative'
            else:
                self.sentiment_label = 'neutral'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Feedback for {self.test_attempt.test.name} by {self.teacher.username}"