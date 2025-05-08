# attempt_test/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import TestAttempt, QuestionAttempt
from create_test.models import Test
from question_bank.models import MCQ
from django.utils import timezone

def get_options(mcq):
    """Get all options for a question in a list."""
    return [mcq.option_a, mcq.option_b, mcq.option_c, mcq.option_d]

@login_required
def view_tests(request):
    # Fetch published tests that are visible to the students
    tests = Test.objects.filter(is_published=True)  # Only show published tests

    return render(request, 'attempt_test/view_tests.html', {
        'tests': tests  # Pass the tests to the template
    })
    

@login_required
def attempt_test(request, test_id, question_index=1):
    test = get_object_or_404(Test, id=test_id)
    questions = test.test_mcqs.all()

    try:
        current_question = questions[question_index - 1]
    except IndexError:
        return redirect('attempt_test:result', test_attempt_id=request.session.get('test_attempt_id'))

    # Get or create test attempt
    test_attempt, created = TestAttempt.objects.get_or_create(
        user=request.user, test=test, is_completed=False,
        defaults={'start_time': timezone.now()}  # Set start_time when creating new attempt
    )
    
    # Initialize remaining_seconds
    total_duration_seconds = test.duration * 60  # Convert minutes to seconds
    
    # If test was already started, calculate remaining time
    if test_attempt.start_time:
        elapsed_time = timezone.now() - test_attempt.start_time
        remaining_seconds = max(0, total_duration_seconds - int(elapsed_time.total_seconds()))
    else:
        # If no start time (shouldn't happen with defaults above, but just in case)
        remaining_seconds = total_duration_seconds
        test_attempt.start_time = timezone.now()
        test_attempt.save()

    # If time is up, automatically complete the test
    if remaining_seconds <= 0:
        test_attempt.is_completed = True
        test_attempt.save()
        return redirect('attempt_test:result', test_attempt_id=test_attempt.id)

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        time_expired = request.POST.get('time_expired') == 'true'

        if time_expired:
            test_attempt.is_completed = True
            test_attempt.save()
            return redirect('attempt_test:result', test_attempt_id=test_attempt.id)

        if not selected_option:
            return render(request, 'attempt_test/attempt_test.html', {
                'test': test,
                'question': current_question.mcq,
                'current_question_index': question_index,
                'total_questions': len(questions),
                'remaining_seconds': remaining_seconds,
                'error_message': 'Please select an option before proceeding.'
            })

        # Get the correct answer text based on the correct_answer letter
        correct_answer_text = getattr(current_question.mcq, f'option_{current_question.mcq.correct_answer.lower()}')
        selected_answer_text = getattr(current_question.mcq, f'option_{selected_option.lower()}')

        question_attempt = QuestionAttempt.objects.create(
            test_attempt=test_attempt,
            question=current_question.mcq,
            selected_option=selected_option,
            is_correct=(selected_answer_text == correct_answer_text)
        )

        if question_index < len(questions):
            return redirect('attempt_test:attempt_test', test_id=test.id, question_index=question_index + 1)
        else:
            test_attempt.is_completed = True
            test_attempt.save()
            return redirect('attempt_test:result', test_attempt_id=test_attempt.id)

    return render(request, 'attempt_test/attempt_test.html', {
        'test': test,
        'question': current_question.mcq,
        'current_question_index': question_index,
        'total_questions': len(questions),
        'remaining_seconds': remaining_seconds,
        'error_message': None
    })


def test_result(request, test_attempt_id):
    test_attempt = get_object_or_404(TestAttempt, id=test_attempt_id)
    test = test_attempt.test

    # Calculate time taken
    if test_attempt.start_time:
        time_taken = test_attempt.updated_at - test_attempt.start_time
        total_seconds = int(time_taken.total_seconds())
        
        # Calculate hours, minutes, and seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        # Create time taken string
        time_parts = []
        if hours > 0:
            time_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            time_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not time_parts:  # Include seconds if it's the only unit or if there are seconds
            time_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        time_taken_str = " ".join(time_parts)
    else:
        time_taken_str = "Time not available"

    # Get all question attempts
    question_attempts = test_attempt.question_attempts.all()
    total_questions = len(question_attempts)
    
    # Calculate score and percentage
    correct_answers = sum(1 for qa in question_attempts if qa.is_correct)
    score = correct_answers
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Check if passed based on test's pass mark
    is_passed = percentage >= test.pass_mark

    # Update test attempt with final results
    test_attempt.score = score
    test_attempt.percentage = percentage
    test_attempt.is_completed = True
    test_attempt.save()

    # Prepare question attempts with option data
    for qa in question_attempts:
        # Get the correct answer text
        correct_answer_letter = qa.question.correct_answer.lower()
        qa.correct_answer_text = getattr(qa.question, f'option_{correct_answer_letter}')
        
        # Get the selected answer text
        selected_answer_letter = qa.selected_option.lower()
        qa.selected_answer_text = getattr(qa.question, f'option_{selected_answer_letter}')
        
        # Add all options in a list for easy access
        qa.all_options = [
            ('A', qa.question.option_a),
            ('B', qa.question.option_b),
            ('C', qa.question.option_c),
            ('D', qa.question.option_d)
        ]

    # Pass the correct values to the template
    return render(request, 'attempt_test/test_result.html', {
        'test_attempt': test_attempt,
        'test': test,
        'score': score,
        'total_questions': total_questions,
        'percentage': percentage,
        'time_taken': time_taken_str,
        'is_passed': is_passed,
        'page_title': 'Test Result - MCQ Test System',
        'question_attempts': question_attempts
    })
