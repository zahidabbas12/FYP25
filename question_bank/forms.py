# forms.py
from django import forms
from .models import MCQ

class MCQForm(forms.ModelForm):
    class Meta:
        model = MCQ
        fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation', 'difficulty', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to each field
        self.fields['question'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['option_a'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['option_b'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['option_c'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['option_d'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['correct_answer'].widget.attrs.update({'class': 'form-select form-select-sm'})
        self.fields['explanation'].widget.attrs.update({'class': 'form-control form-control-sm'})
        self.fields['difficulty'].widget.attrs.update({'class': 'form-select form-select-sm'})
        self.fields['category'].widget.attrs.update({'class': 'form-select form-select-sm'})