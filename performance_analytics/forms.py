from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['content']  
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'cols': 50}),
        }

    def save(self, commit=True):
        feedback = super().save(commit=False)
        if commit:
            feedback.save()
        return feedback
