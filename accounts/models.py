# accounts/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="Upload a profile picture (optional)"
    )
    
    # Override to ensure email is required and unique
    email = models.EmailField(unique=True, blank=False)

    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default-profile.png'

    def save(self, *args, **kwargs):
        # Delete old profile picture when updating
        if self.pk:
            try:
                old_user = CustomUser.objects.get(pk=self.pk)
                if old_user.profile_picture and self.profile_picture != old_user.profile_picture:
                    old_user.profile_picture.delete(save=False)
            except CustomUser.DoesNotExist:
                pass
        super().save(*args, **kwargs)
