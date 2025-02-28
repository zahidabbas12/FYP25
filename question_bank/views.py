from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MCQ
from .forms import MCQForm
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import DatabaseError

@login_required
def manage_questions(request):
    """Displays and allows teachers to manage questions."""
    try:
        if not (request.user.role == 'teacher' or request.user.is_superuser):
            return HttpResponseForbidden("You are not allowed to access this page.")

        categories = dict(MCQ.CATEGORY_CHOICES).keys()
        category_filter = request.GET.get('category', None)

        # Handle the category filter logic
        if category_filter:
            mcqs = MCQ.objects.filter(teacher=request.user, category=category_filter) if request.user.role == 'teacher' else MCQ.objects.filter(category=category_filter)
        else:
            mcqs = MCQ.objects.filter(teacher=request.user) if request.user.role == 'teacher' else MCQ.objects.all()

        # Pagination setup (10 items per page)
        paginator = Paginator(mcqs, 10)  # Show 10 questions per page
        page_number = request.GET.get('page')  # Get current page number from query params

        # Handle page number errors, if the page is invalid, show the last page
        try:
            page_obj = paginator.get_page(page_number)
        except Exception as e:
            # Log the error (you could log it to a file or monitoring service)
            print(f"Error with pagination: {e}")
            page_obj = paginator.get_page(1)  # Default to the first page

        return render(request, 'question_bank/manage_questions.html', {
            'page_obj': page_obj,
            'categories': categories,
            'category_filter': category_filter,
            'page_title': ' Manage Questions - MCQ Test System'
        })

    except DatabaseError as db_error:
        # Handle database errors, log them for debugging
        print(f"Database error: {db_error}")
        return render(request, 'error.html', {'error_message': 'There was a problem with the database. Please try again later.'})

    except Exception as e:
        # Handle other unexpected errors
        print(f"Unexpected error: {e}")
        return render(request, 'error.html', {'error_message': 'An unexpected error occurred. Please try again later.'})

@login_required
def add_question(request):
    if request.method == "POST":
        question = request.POST['question']
        option_a = request.POST['option_a']
        option_b = request.POST['option_b']
        option_c = request.POST['option_c']
        option_d = request.POST['option_d']
        correct_answer = request.POST['correct_answer']
        explanation = request.POST['explanation']
        difficulty = request.POST['difficulty']
        category = request.POST['category']

        if request.user.role != 'teacher' and not request.user.is_superuser:
            return HttpResponseForbidden("You do not have permission to add questions.")
        
        if category not in dict(MCQ.CATEGORY_CHOICES).keys():
            return HttpResponseForbidden("Invalid category.")

        mcq = MCQ(
            question=question,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty=difficulty,
            category=category,
            teacher=request.user
        )
        mcq.save()
        return redirect('manage_questions')

    categories = MCQ.CATEGORY_CHOICES  # Send the choices directly
    return render(request, 'question_bank/add_question.html', {
        'categories': categories,
        'page_title': 'Add Questions - MCQ Test System',
    })



@login_required
def edit_question(request, id):
    """Allows teachers to edit their own question."""
    mcq = get_object_or_404(MCQ, id=id)
    
    if not (request.user == mcq.teacher or request.user.is_superuser):
        return HttpResponseForbidden("You are not allowed to edit this question.")

    if request.method == 'POST':
        form = MCQForm(request.POST, instance=mcq)
        if form.is_valid():
            form.save()
            return redirect('manage_questions')
    else:
        form = MCQForm(instance=mcq)

    # Pass the categories to the template
    categories = [category[0] for category in MCQ.CATEGORY_CHOICES]
    return render(request, 'question_bank/edit_question.html', {
        'form': form,
        'categories': categories  # Ensure categories are passed to the template
    })
    

@login_required
def delete_question(request, id):
    """Allows teachers to delete their own question."""
    mcq = get_object_or_404(MCQ, id=id)
    
    if not (request.user == mcq.teacher or request.user.is_superuser):
        return HttpResponseForbidden("You are not allowed to delete this question.")

    if request.method == 'POST':
        mcq.delete()
        return redirect('manage_questions')
    return redirect('teacher_dashboard')


@login_required
def update_category(request, mcq_id):
    """Updates the category of an existing question."""
    if request.method == "POST":
        mcq = get_object_or_404(MCQ, id=mcq_id)
        
        if not (request.user == mcq.teacher or request.user.is_superuser):
            return HttpResponseForbidden("You are not allowed to update this question.")
        
        new_category = request.POST.get('category')
        
        if new_category in dict(MCQ.CATEGORY_CHOICES).keys():
            mcq.category = new_category
            mcq.save()

    return redirect('manage_questions')
