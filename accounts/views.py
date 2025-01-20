from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomeUserCreationForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from create_test.models import Test
from question_bank.models import MCQ

def home(request):
    return render(request, 'accounts/home.html')

@login_required
def redirect_dashboard(request):
    if request.user.role == 'teacher' or request.user.is_superuser:
        return redirect('teacher_dashboard')
    else:
        return redirect('student_dashboard')

def register(request):
    if request.method == 'POST':
        form = CustomeUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account Created Successfully! You are now logged in")
            return redirect('redirect_dashboard')
        else:
            messages.error(request, "Error creating your account")
    else:
        form = CustomeUserCreationForm()
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
    return render(request, 'accounts/teacher_dashboard.html', {'total_students': total_students, 'total_tests': total_tests, 'total_questions': total_questions})

@login_required
def student_dashboard(request):
    return render(request, 'accounts/student_dashboard.html')

@login_required
def profile_view(request):
    user = request.user
    return render(request, 'accounts/profile', {'user': user})

@login_required
def profile_edit(request):
    if request.method == 'POST':
            form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile_view')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def profile_delete(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Account deleted successfully!")
        return redirect('login')
    return render(request, 'accounts/profile_delete.html')