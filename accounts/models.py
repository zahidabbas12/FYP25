# accounts/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='teacher')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Override to ensure email is required and unique
    email = models.EmailField(unique=True, blank=False)

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default-profile.png'
