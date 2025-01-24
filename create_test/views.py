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
        test_form = TestForm(request.POST)  # Form to create the test
        mcqs_selected = request.POST.getlist('mcqs')  # Get the list of selected MCQs from the checkboxes

        if test_form.is_valid():
            # Debugging: Print the cleaned data for testing
            print(test_form.cleaned_data)

            # Save the test, but don't commit yet
            test = test_form.save(commit=False)
            test.teacher = request.user  # Assign the teacher to the created test

            # Ensure 'is_published' is handled from the form
            test.is_published = test_form.cleaned_data.get('is_published', False)

            test.save()  # Save the test

            # Now, associate the selected MCQs with the test using the TestMCQ model
            for order, mcq_id in enumerate(mcqs_selected, start=1):
                mcq = MCQ.objects.get(id=mcq_id)  # Fetch the MCQ by ID
                TestMCQ.objects.create(test=test, mcq=mcq, order=order)  # Associate MCQs with the test

            # Redirect to manage_tests after saving the test and its MCQs
            return redirect('manage_tests')  # Redirect to the manage_tests page
        else:
            return render(request, 'create_test/create_test.html', {
                'test_form': test_form,
                'error_message': "Form is invalid. Please correct the errors."
            })
    
    else:
        test_form = TestForm()  # Empty form for GET request

    # Query all MCQs to pass them to the template
    all_mcqs = MCQ.objects.all()

    return render(request, 'create_test/create_test.html', {
        'test_form': test_form,
        'all_mcqs': all_mcqs  # Pass the MCQs to the template
    })

@login_required
def manage_tests(request):
    tests = Test.objects.filter(teacher=request.user)
    return render(request, 'create_test/manage_tests.html', {'tests': tests})

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
        # Handle form submission for updating the test
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()  # Save the updated test details
            return redirect('manage_tests')  # Redirect to the manage_tests page after saving

        # Handle MCQ deletion
        if 'delete_mcq' in request.POST:
            mcq_id = request.POST.get('mcq_id')  # Get the ID of the MCQ to delete
            try:
                test_mcq = TestMCQ.objects.get(id=mcq_id, test=test)  # Get the TestMCQ object
                test_mcq.delete()  # Delete the TestMCQ object, which removes the MCQ from the test
                return redirect('edit_test', test_id=test.id)  # Redirect to the same page to update the list
            except TestMCQ.DoesNotExist:
                pass  # Handle the case where the MCQ doesn't exist or can't be deleted

    else:
        form = TestForm(instance=test)  # Get the form for displaying the test details

    return render(request, 'create_test/edit_test.html', {
        'form': form,
        'test': test,
        'test_mcqs': test_mcqs  # Pass the list of MCQs associated with this test
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