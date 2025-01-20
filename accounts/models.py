from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Teacher', 'Teacher'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='teacher')
    proile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    email = models.EmailField(unique=True, blank=False)

    def get_profile_picture(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default-profile.png'