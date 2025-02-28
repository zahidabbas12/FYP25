# attempt_test/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import TestAttempt, QuestionAttempt
from create_test.models import Test
from question_bank.models import MCQ
from django.utils import timezone

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

        question_attempt = QuestionAttempt.objects.create(
            test_attempt=test_attempt,
            question=current_question.mcq,
            selected_option=selected_option,
            is_correct=(selected_option == current_question.mcq.correct_answer)
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

    # Calculate score and percentage
    score = 0
    total_questions = test_attempt.question_attempts.count()

    for qa in test_attempt.question_attempts.all():
        if qa.is_correct:
            score += 1
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0

    # Save results
    test_attempt.score = score
    test_attempt.percentage = percentage
    test_attempt.is_completed = True
    test_attempt.save()

    # Pass the correct values to the template, including the answers and correctness
    return render(request, 'attempt_test/test_result.html', {
        'test_attempt': test_attempt,
        'score': score,
        'total_questions': total_questions,
        'percentage': percentage,
        'time_taken': time_taken_str,  # Make sure this is being passed
        'page_title': 'Test Result - MCQ Test System',
        'question_attempts': test_attempt.question_attempts.all()  # Pass the question attempts to the template
    })
