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


def home(request):
    """Landing page for all users."""
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
            return redirect('redirect_dashboard')
        else:
            messages.error(request, "There was an error with your registration. Please correct the highlighted fields.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, "You have successfully logged in.")
        return redirect('redirect_dashboard')
    elif request.method == 'POST':
        messages.error(request, "Invalid username or password. Please try again.")
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)  
    return redirect('home')


@login_required
def teacher_dashboard(request):
    total_students = CustomUser.objects.filter(role='student').count()
    total_tests = Test.objects.filter(teacher=request.user).count()
    total_questions = MCQ.objects.filter(teacher=request.user).count()
    return render(request, 'accounts/teacher_dashboard.html', {
        'total_students': total_students,
        'total_tests': total_tests,
        'total_questions': total_questions
    })


@login_required
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')

@login_required
def profile_view(request):
    user = request.user
    # Additional user data can be added like 'subjects' and 'test attempts' by querying related models.
    return render(request, 'accounts/profile_view.html', {'user': user})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_view')  # Redirect to the profile view after saving
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def profile_delete(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('login')
    return render(request, 'accounts/profile_delete.html')