# attempt_test/forms.py
from django import forms
from question_bank.models import MCQ

class QuestionAttemptForm(forms.Form):
    def __init__(self, *args, **kwargs):
        test = kwargs.pop('test', None)
        super(QuestionAttemptForm, self).__init__(*args, **kwargs)

        # Dynamically add the question fields based on the test questions
        for question in test.questions.all():
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                choices=[
                    ('A', question.option_a),
                    ('B', question.option_b),
                    ('C', question.option_c),
                    ('D', question.option_d),
                ],
                widget=forms.RadioSelect
            )
