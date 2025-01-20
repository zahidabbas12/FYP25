from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Test, TestMCQ, MCQ
from question_bank.models import MCQ
from .forms import TestForm, AddMCQToTestForm 

@login_required 
def create_test(request):
    """View for creating and managing a test"""
    if request.method == "POST":
        test_form = TestForm(request.POST)
        mcq_form = AddMCQToTestForm(request.POST)
        
        if test_form.is_valid():
            # Save test and link it to the logged-in teacher
            test = test_form.save(commit=False)
            test.teacher = request.user  # Assign the teacher to the created test
            test.save()  # Save the test

            # Redirect to manage_tests after saving the test
            return redirect('manage_tests')  # Redirect to the manage_tests page
        
        else:
            return HttpResponse('Form is invalid', status=400)
    
    else:
        test_form = TestForm()
        mcq_form = AddMCQToTestForm()

    # Query all MCQs
    all_mcqs = MCQ.objects.all()

    return render(request, 'create_test/create_test.html', {
        'test_form': test_form,
        'mcq_form': mcq_form,
        'all_mcqs': all_mcqs  # Pass the MCQs to the template
    })

@login_required
def manage_tests(request):
    tests = Test.objects.filter(teacher=request.user)
    return render(request, 'create_test/manage_test.html', {'tests': tests})

@login_required
def add_mcqs_to_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)  # Fetch the Test object by its ID
    
    # Ensure the user is the teacher (logged-in user is assumed to be the teacher)
    teacher = request.user  # Assuming the user is a teacher, adjust if needed
    
    # Get the first 2 MCQs created by the teacher
    first_two_mcqs = MCQ.objects.filter(teacher=teacher)[:2]
    
    # Add the first 2 MCQs to the test with order 1 and 2
    for i, mcq in enumerate(first_two_mcqs):
        TestMCQ.objects.create(test=test, mcq=mcq, order=i + 1)
            
    # Redirect to the edit test page
    return redirect('edit_test', test_id=test.id)  # Change redirect to edit_test instead of manage_tests

    # Fetch all the MCQs associated with the teacher
    mcqs = MCQ.objects.filter(teacher=teacher)

    return render(request, 'create_test/add_mcqs.html', {
        'form': form,
        'mcqs': mcqs,
        'test': test
    })


@login_required
def edit_test(request, test_id):
    test = get_object_or_404(Test, id=test_id, teacher=request.user)

    # Fetch all the MCQs that are associated with this test
    test_mcqs = TestMCQ.objects.filter(test=test).order_by('order')  # Order MCQs based on 'order'

    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)  # Use your Test form here
        if form.is_valid():
            form.save()
            return redirect('manage_tests')  # Redirect to 'manage_tests' instead of 'edit_test' after saving
    else:
        form = TestForm(instance=test)

    return render(request, 'create_test/edit_test.html', {
        'form': form,
        'test': test,
        'test_mcqs': test_mcqs  # Pass the list of MCQs added to the test
    })

@login_required
def delete_test(request, test_id):
    """
    View to delete a test with no confirmation page.
    """
    test = get_object_or_404(Test, id=test_id, teacher=request.user)
    if request.method == "POST":
        test.delete()
        return redirect('manage_tests')  # Redirect to the tests list page
    else:
        # You can add a message or a response here to confirm it's being deleted
        return redirect('manage_tests')