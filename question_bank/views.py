from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import MCQ
from .forms import MCQForm
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import DatabaseError
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk import FreqDist
import random
import spacy
from django.contrib import messages

# Ensure the 'punkt' data is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

@login_required
def manage_questions(request):
    """Displays and allows teachers to manage questions."""
    try:
        if not (request.user.role == 'teacher' or request.user.is_superuser):
            return HttpResponseForbidden("You are not allowed to access this page.")

        categories = dict(MCQ.CATEGORY_CHOICES).keys()
        category_filter = request.GET.get('category', None)
        search_query = request.GET.get('search', '')  # Get the search query

        # Handle the category filter and search logic
        if category_filter:
            mcqs = MCQ.objects.filter(teacher=request.user, category=category_filter) if request.user.role == 'teacher' else MCQ.objects.filter(category=category_filter)
        else:
            mcqs = MCQ.objects.filter(teacher=request.user) if request.user.role == 'teacher' else MCQ.objects.all()

        if search_query:
            mcqs = mcqs.filter(question__icontains=search_query)  # Filter by search query

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
        messages.success(request, 'Question deleted successfully.')
        return redirect('manage_questions')
    return redirect('manage_questions')

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

import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def generate_mcqs(request):
    if request.method == "POST":
        text = request.POST.get('text', '')
        if not text:
            return render(request, 'question_bank/generate_mcqs.html', {
                'error_message': 'Please provide text to generate MCQs.'
            })

        # Process the text with spaCy
        doc = nlp(text)

        # Generate MCQs
        mcqs = []
        for sentence in doc.sents:
            if len(mcqs) >= 10:
                break  # Limit to 10 questions

            # Extract nouns and proper nouns
            words = [token.text for token in sentence if token.pos_ in ['NOUN', 'PROPN']]
            unique_words = list(set(words))
            if len(unique_words) < 4:
                continue  # Not enough to create options

            # Select correct answer and options
            correct_answer = random.choice(unique_words)
            distractors = [w for w in unique_words if w != correct_answer]
            if len(distractors) < 3:
                continue  # Ensure enough distractors

            options = random.sample(distractors, 3) + [correct_answer]
            random.shuffle(options)

            # Capitalize all options
            options = [opt.capitalize() for opt in options]

            option_map = {chr(65 + i): option for i, option in enumerate(options)}
            correct_option = next(k for k, v in option_map.items() if v.lower() == correct_answer.lower())

            # Replace first occurrence of correct_answer with a blank
            question_text = sentence.text.replace(correct_answer, "_____", 1)

            # Try to determine the grammatical role of the correct answer
            token_info = next((token for token in sentence if token.text == correct_answer), None)
            if token_info:
                role = token_info.dep_
                if role == 'nsubj':
                    role_description = "the subject of the sentence, which performs the action"
                elif role == 'dobj':
                    role_description = "the object of the sentence, which receives the action"
                elif role == 'pobj':
                    role_description = "the object of a preposition, adding detail to the context"
                else:
                    role_description = "an important noun that contributes to the sentence's meaning"

                explanation = (
                    f"The correct answer is '{correct_answer}' because it is {role_description}. "
                    f"In the sentence: \"{sentence.text}\", this word is essential to understanding the overall meaning."
                )
            else:
                explanation = (
                    f"The correct answer is '{correct_answer}', which best fits the blank based on the context of the sentence: "
                    f"\"{sentence.text}\"."
                )

            # Detect category (fallback to 'General')
            category = 'General'
            for cat, _ in MCQ.CATEGORY_CHOICES:
                if cat.lower() in sentence.text.lower():
                    category = cat
                    break

            mcqs.append({
                'question': question_text,
                'options': option_map,
                'correct_answer': correct_option,
                'explanation': explanation,
                'difficulty': 'Medium',
                'category': category
            })

        return render(request, 'question_bank/select_mcqs.html', {
            'mcqs': mcqs,
            'categories': MCQ.CATEGORY_CHOICES
        })

    return render(request, 'question_bank/generate_mcqs.html')

@login_required
def save_mcqs(request):
    if request.method == "POST":
        questions = request.POST.getlist('questions')
        correct_answers = request.POST.getlist('correct_answers')
        explanations = request.POST.getlist('explanations')
        difficulties = request.POST.getlist('difficulties')
        categories = request.POST.getlist('categories')
        selected_mcqs = request.POST.getlist('selected_mcqs')

        for index, question in enumerate(questions):
            if question in selected_mcqs:
                # Get all options for the current question
                options = []
                for i in range(4):  # Get all 4 options
                    option_key = f'option_{index}_{chr(65+i)}'  # Creates option_0_A, option_0_B, etc.
                    option_value = request.POST.get(option_key, '')
                    if not option_value:  # Skip if option is empty
                        continue
                    options.append(option_value)

                # Validate that we have exactly 4 options
                if len(options) != 4:
                    messages.error(request, f'Question {index + 1} must have exactly 4 options.')
                    continue

                # Create the MCQ with the edited values
                mcq = MCQ(
                    question=question,
                    option_a=options[0],
                    option_b=options[1],
                    option_c=options[2],
                    option_d=options[3],
                    correct_answer=correct_answers[index],
                    explanation=explanations[index],
                    difficulty=difficulties[index],
                    category=categories[index],
                    teacher=request.user
                )
                try:
                    mcq.save()
                    messages.success(request, f'Successfully saved question {index + 1}.')
                except Exception as e:
                    messages.error(request, f'Error saving question {index + 1}: {str(e)}')

        return redirect('manage_questions')

    return HttpResponseForbidden("Invalid request method.")

@login_required
def delete_generated_mcqs(request):
    if request.method == "POST":
        selected_mcqs = request.POST.getlist('selected_mcqs')
        # Get all questions from the session
        questions = request.POST.getlist('questions')
        
        # Filter out the selected MCQs and keep the rest
        remaining_mcqs = []
        for index, question in enumerate(questions):
            if question not in selected_mcqs:
                # Reconstruct MCQ object for non-deleted questions
                mcq = {
                    'question': question,
                    'options': {},
                    'explanation': request.POST.getlist('explanations')[index],
                    'difficulty': request.POST.getlist('difficulties')[index],
                    'category': request.POST.getlist('categories')[index],
                    'correct_answer': request.POST.getlist('correct_answers')[index]
                }
                # Reconstruct options
                for i in range(4):
                    option_key = f'option_{index}_{chr(65+i)}'
                    mcq['options'][chr(65+i)] = request.POST.get(option_key, '')
                remaining_mcqs.append(mcq)

        # Render the same page with remaining MCQs
        return render(request, 'question_bank/select_mcqs.html', {
            'mcqs': remaining_mcqs,
            'categories': MCQ.CATEGORY_CHOICES
        })

    return HttpResponseForbidden("Invalid request method.")

@login_required
def delete_selected_questions(request):
    if request.method == "POST":
        selected_questions = request.POST.getlist('selected_questions')
        MCQ.objects.filter(id__in=selected_questions, teacher=request.user).delete()
        return redirect('manage_questions')

    return HttpResponseForbidden("Invalid request method.")
