from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MCQ
from .forms import MCQForm
from django.http import HttpResponseForbidden


@login_required
def manage_questions(request):
    """Displays and allows teachers to manage questions."""
    if not (request.user.role == 'teacher' or request.user.is_superuser):
        return HttpResponseForbidden("You are not allowed to access this page.")
    
    categories = dict(MCQ.CATEGORY_CHOICES).keys()
    category_filter = request.GET.get('category', None)
    
    if category_filter:
        mcqs = MCQ.objects.filter(teacher=request.user, category=category_filter) if request.user.role == 'teacher' else MCQ.objects.filter(category=category_filter)
    else:
        mcqs = MCQ.objects.filter(teacher=request.user) if request.user.role == 'teacher' else MCQ.objects.all()

    return render(request, 'question_bank/manage_questions.html', {
        'mcqs': mcqs,
        'categories': categories,
        'category_filter': category_filter
    })


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
        'categories': categories
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
