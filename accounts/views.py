from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from .models import CustomUser  
from django.core.exceptions import PermissionDenied
from create_test.models import Test
from question_bank.models import MCQ
from create_test import views
from django.db.models import Avg


def home(request):
    """Landing page for all users."""
    if request.user.is_authenticated:
        if request.user.role == 'teacher' or request.user.is_superuser:
            return redirect('teacher_dashboard')
        elif request.user.role == 'student':
            return redirect('student_dashboard')
    return render(request, 'accounts/home.html')

@login_required
def redirect_dashboard(request):
    if request.user.role == 'teacher':
        return redirect('teacher_dashboard')
    elif request.user.role == 'student':
        return redirect('student_dashboard')
    else:
        raise PermissionDenied("Invalid user role.")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! You are now logged in.")
            if user.role == 'teacher' or user.is_superuser:
                return redirect('teacher_dashboard')
            elif user.role == 'student':
                return redirect('student_dashboard')
        else:
            messages.error(request, "There was an error with your registration. Please correct the highlighted fields.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form, 'page_title': 'Register - MCQ Test System'})

def login_view(request):
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        # Set initial last activity time as ISO format string
        request.session['last_activity'] = timezone.now().isoformat()
        messages.success(request, "You have successfully logged in.")
        if user.role == 'teacher' or user.is_superuser:
            return redirect('teacher_dashboard')
        elif user.role == 'student':
            return redirect('student_dashboard')
    elif request.method == 'POST':
        messages.error(request, "Invalid username or password. Please try again.")
    return render(request, 'accounts/login.html', {'form': form, 'page_title': 'Login- MCQ Test System'})

def logout_view(request):
    logout(request)  
    return redirect('home')


@login_required
def teacher_dashboard(request):
    if not (request.user.role == 'teacher' or request.user.is_superuser):
        return redirect('home')

    # Get the total number of registered students
    total_students = CustomUser.objects.filter(role='student').count()

    # Fetch all registered students with their test attempts
    students = CustomUser.objects.filter(role='student').prefetch_related('testattempt_set')

    # Fetch the total number of tests and questions created by the teacher
    total_tests = Test.objects.filter(teacher=request.user).count()
    total_questions = MCQ.objects.filter(teacher=request.user).count()

    # Calculate statistics for each student
    students_data = []
    for student in students:
        # Get all test attempts for this student
        test_attempts = student.testattempt_set.all()
        
        if test_attempts.exists():
            # Calculate average percentage (not score)
            avg_percentage = test_attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
            avg_percentage = round(avg_percentage, 1)
            
            # Get the most recent attempt
            last_attempt = test_attempts.order_by('-attempt_date').first()
            
            students_data.append({
                'student': student,
                'total_attempts': test_attempts.count(),
                'avg_score': avg_percentage,  # This is actually percentage
                'last_attempt': last_attempt.attempt_date if last_attempt else None,
            })
        else:
            # If no attempts, add student with zero values
            students_data.append({
                'student': student,
                'total_attempts': 0,
                'avg_score': 0,
                'last_attempt': None,
            })

    # Sort students by average score in descending order
    students_data.sort(key=lambda x: x['avg_score'], reverse=True)

    # Pass the enhanced context to the template
    return render(request, 'accounts/teacher_dashboard.html', {
        'total_students': total_students,
        'students_data': students_data,
        'total_tests': total_tests,
        'total_questions': total_questions,
        'page_title': f"{request.user}'s Dashboard - MCQ Test System",
    })


@login_required
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')

@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user,
        'page_title': f"{user.username}'s Profile - MCQ Test System",
        'total_tests': user.testattempt_set.count() if user.role == 'student' else Test.objects.filter(teacher=user).count(),
        'avg_score': user.testattempt_set.aggregate(Avg('score'))['score__avg'] if user.role == 'student' else None,
    }
    return render(request, 'accounts/profile_view.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile_view')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileEditForm(instance=request.user)
    
    context = {
        'form': form,
        'page_title': 'Edit Profile - MCQ Test System',
    }
    return render(request, 'accounts/profile_edit.html', context)

@login_required
def profile_delete(request):
    user = request.user
    if request.method == 'POST':
        try:
            # Delete profile picture if it exists
            if user.profile_picture:
                user.profile_picture.delete(save=False)
            
            # Delete the user account
            user.delete()
            messages.success(request, "Your account has been deleted successfully.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"An error occurred while deleting your account: {str(e)}")
            return redirect('profile_view')
    
    context = {
        'page_title': 'Delete Profile - MCQ Test System'
    }
    return render(request, 'accounts/profile_delete.html', context)