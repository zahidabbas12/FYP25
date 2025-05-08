from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Test, TestMCQ, MCQ
from question_bank.models import MCQ
from .forms import TestForm, AddMCQToTestForm 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db.models import Max



@login_required
def create_test(request):
    """View for creating and managing a test"""
    if request.method == "POST":
        test_form = TestForm(request.POST)
        mcqs_selected = request.POST.getlist('mcqs')

        # Check if at least 2 questions are selected
        if len(mcqs_selected) < 2:
            messages.error(request, 'Please select at least 2 questions for the test.')
            # Get both own MCQs and other teachers' MCQs
            own_mcqs = MCQ.objects.filter(teacher=request.user)
            other_mcqs = MCQ.objects.exclude(teacher=request.user)
            all_mcqs = own_mcqs.union(other_mcqs)
            categories = dict(MCQ.CATEGORY_CHOICES)
            return render(request, 'create_test/create_test.html', {
                'test_form': test_form,
                'all_mcqs': all_mcqs,
                'categories': MCQ.CATEGORY_CHOICES,
                'error_message': "Minimum 2 questions required."
            })

        if test_form.is_valid():
            test = test_form.save(commit=False)
            test.teacher = request.user
            test.is_published = test_form.cleaned_data.get('is_published', False)
            test.save()

            # Associate the selected MCQs with the test
            for order, mcq_id in enumerate(mcqs_selected, start=1):
                mcq = MCQ.objects.get(id=mcq_id)
                TestMCQ.objects.create(test=test, mcq=mcq, order=order)

            messages.success(request, 'Test created successfully!')
            return redirect('manage_tests')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        test_form = TestForm()

    # Get both own MCQs and other teachers' MCQs
    own_mcqs = MCQ.objects.filter(teacher=request.user)
    other_mcqs = MCQ.objects.exclude(teacher=request.user)
    all_mcqs = own_mcqs.union(other_mcqs)
    
    return render(request, 'create_test/create_test.html', {
        'test_form': test_form,
        'all_mcqs': all_mcqs,
        'categories': MCQ.CATEGORY_CHOICES,
        'page_title': 'Create Tests - MCQ Test System'
    })

@login_required
def manage_tests(request):
    # Get all tests related to the logged-in teacher
    search_query = request.GET.get('search', '')  # Get the search query
    tests = Test.objects.filter(teacher=request.user)

    if search_query:
        tests = tests.filter(title__icontains=search_query)  # Filter by search query

    # Set up pagination (10 items per page)
    paginator = Paginator(tests, 10)  # Show 10 tests per page
    page_number = request.GET.get('page')  # Get current page number from query params
    page_obj = paginator.get_page(page_number)

    # Render the page with the paginated tests
    return render(request, 'create_test/manage_tests.html', {
        'page_obj': page_obj,  # Pass the paginated tests to the template
        'page_title': 'Manage Tests- MCQ Test System'
    })

@login_required
def add_mcqs_to_test(request, test_id):
    test = get_object_or_404(Test, id=test_id, teacher=request.user)
    
    # Get existing MCQ IDs for this test
    existing_mcq_ids = set(TestMCQ.objects.filter(test=test).values_list('mcq_id', flat=True))
    
    if request.method == "POST":
        selected_mcqs = request.POST.getlist('selected_mcqs')
        if selected_mcqs:
            # Get the highest current order
            max_order = TestMCQ.objects.filter(test=test).aggregate(Max('order'))['order__max'] or 0
            
            # Add new MCQs
            for i, mcq_id in enumerate(selected_mcqs, start=1):
                # Skip if MCQ is already in the test
                if int(mcq_id) not in existing_mcq_ids:
                    mcq = get_object_or_404(MCQ, id=mcq_id)
                    TestMCQ.objects.create(
                        test=test,
                        mcq=mcq,
                        order=max_order + i
                    )
            
            messages.success(request, f'{len(selected_mcqs)} question(s) added successfully.')
        else:
            messages.warning(request, 'No questions were selected.')
        
        return redirect('edit_test', test_id=test.id)
    
    # For GET request, show the selection page
    # Get both own MCQs and other teachers' MCQs
    own_mcqs = MCQ.objects.filter(teacher=request.user)
    other_mcqs = MCQ.objects.exclude(teacher=request.user)
    
    # Combine both querysets
    available_mcqs = own_mcqs.union(other_mcqs)
    categories = MCQ.CATEGORY_CHOICES
    
    context = {
        'test': test,
        'available_mcqs': available_mcqs,
        'existing_mcq_ids': existing_mcq_ids,
        'categories': categories,
        'page_title': f'Add Questions to {test.title}'
    }
    
    return render(request, 'create_test/add_mcqs.html', context)

@login_required
def edit_test(request, test_id):
    """
    View for editing an existing test and managing its MCQs.
    """
    test = get_object_or_404(Test, id=test_id, teacher=request.user)
    test_mcqs = TestMCQ.objects.filter(test=test).order_by('order')

    if request.method == 'POST':
        if 'delete_mcq' in request.POST:
            # Handle MCQ deletion
            mcq_id = request.POST.get('mcq_id')
            try:
                test_mcq = TestMCQ.objects.get(id=mcq_id, test=test)
                test_mcq.delete()
                messages.success(request, 'Question removed successfully.')
            except TestMCQ.DoesNotExist:
                messages.error(request, 'Question not found.')
            return redirect('edit_test', test_id=test.id)
        
        elif 'toggle_publish' in request.POST:
            # Handle publish/unpublish toggle
            test.is_published = not test.is_published
            test.save()
            status = "published" if test.is_published else "unpublished"
            messages.success(request, f'Test {status} successfully.')
            return redirect('edit_test', test_id=test.id)
        
        else:
            # Handle test update
            try:
                # Update basic test information
                test.title = request.POST.get('title')
                test.duration = request.POST.get('duration')
                test.pass_mark = request.POST.get('pass_mark')
                test.save()

                # Update MCQ orders
                for test_mcq in test_mcqs:
                    new_order = request.POST.get(f'mcq_order_{test_mcq.id}')
                    if new_order and new_order.isdigit():
                        test_mcq.order = int(new_order)
                        test_mcq.save()

                messages.success(request, 'Test updated successfully.')
                return redirect('manage_tests')

            except Exception as e:
                messages.error(request, f'Error updating test: {str(e)}')
                return redirect('edit_test', test_id=test.id)

    context = {
        'test': test,
        'test_mcqs': test_mcqs,
        'page_title': f'Edit Test: {test.title}'
    }
    return render(request, 'create_test/edit_test.html', context)


@login_required
def delete_test(request, test_id):
    """View to delete a test."""
    try:
        test = get_object_or_404(Test, id=test_id, teacher=request.user)
        if request.method == "POST":
            test_title = test.title  # Store the title before deletion
            test.delete()
            messages.success(request, f'Test "{test_title}" was deleted successfully.')
            return redirect('manage_tests')
        else:
            messages.error(request, 'Invalid request method for deleting test.')
            return redirect('manage_tests')
    except Exception as e:
        messages.error(request, f'Error deleting test: {str(e)}')
        return redirect('manage_tests')