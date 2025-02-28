# question_bank/models.py
from django.db import models
from accounts.models import CustomUser  # Reference to the user

class MCQ(models.Model):
    CATEGORY_CHOICES = [
        ('Math', 'Math'),
        ('Science', 'Science'),
        ('English', 'English'),
        ('History', 'History'),
        ('Algorithms', 'Algorithms'),
        ('Computer Science', 'Computer Science'),
        ('Web Development', 'Web Development'),
        ('Other', 'Other'),
    ]
    
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Reference to teacher
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=1)  # Correct answer identifier (A, B, C, D)
    explanation = models.TextField()  # Explanation of the correct answer
    difficulty = models.CharField(max_length=10)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.question