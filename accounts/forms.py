from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser

class CustomeUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')

class ProfileEditForm(forms.ModelForm):
        class Meta:
            models = CustomUser
            fiels = ['username', 'email', 'profile_picture']
            widgets = {
                'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),   
            }