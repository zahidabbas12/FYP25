from django import forms
from .models import Test, TestMCQ
from question_bank.models import MCQ

class TestForm(forms.ModelForm):
    """Form for creating/editing a Test."""
    class Meta:
        model = Test
        fields = ['title', 'description', 'duration', 'pass_mark', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'duration': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Enter duration in minutes'}),
            'pass_mark': forms.NumberInput(attrs={'min': 1, 'max': 100, 'placeholder': 'Enter pass percentage'}),
        }

class AddMCQToTestForm(forms.Form):
    """Form for selecting MCQs to add to a test."""
    mcq = forms.ModelChoiceField(
        queryset=MCQ.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    order = forms.IntegerField(
        widget=forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
        help_text="Specify the order of the question in the test.",
    )

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)  # Receive teacher argument dynamically
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields['mcq'].queryset = MCQ.objects.filter(teacher=teacher)
