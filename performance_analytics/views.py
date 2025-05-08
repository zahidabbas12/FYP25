# performance_analytics/views.py
from django.shortcuts import render, get_object_or_404, redirect
from attempt_test.models import TestAttempt
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from .forms import FeedbackForm
from .models import TestAttempt, Feedback
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import json
from django.db.models import Avg, Count, F
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse


# try:
#     nltk.data.find('vader_lexicon')
# except LookupError:
#     nltk.download('vader_lexicon')


@login_required
def user_performance(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    print(f"Viewing performance for user: {user.username} (ID: {user_id})")
    print(f"Current user: {request.user.username} (Role: {request.user.role})")
    
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    filter_by = request.GET.get('filter_by', '')
    status_filter = request.GET.get('status', '')
    
    # Check permissions and get appropriate test attempts
    if request.user.role == 'teacher' or request.user.is_superuser:
        # For teachers, show all attempts for tests they created
        test_attempts = TestAttempt.objects.filter(
            test__teacher=request.user
        ).select_related('test', 'user', 'feedback').order_by('-attempt_date')
        print(f"Teacher view - Found {test_attempts.count()} attempts")
    elif request.user.id == user_id:
        # For students, show their own attempts
        test_attempts = TestAttempt.objects.filter(
            user=user
        ).select_related('test', 'user', 'feedback').order_by('-attempt_date')
        print(f"Student view - Found {test_attempts.count()} attempts")
    else:
        return HttpResponseForbidden("You don't have permission to view this page.")

    # Apply search filter if search query exists
    if search_query:
        if filter_by == 'test':
            test_attempts = test_attempts.filter(test__title__icontains=search_query)
        elif filter_by == 'student':
            test_attempts = test_attempts.filter(user__username__icontains=search_query)
        else:
            # Default search across both test name and student name
            test_attempts = test_attempts.filter(
                Q(test__title__icontains=search_query) |
                Q(user__username__icontains=search_query)
            )

    # Apply status filter if selected
    if status_filter:
        if status_filter == 'passed':
            test_attempts = test_attempts.filter(percentage__gte=F('test__pass_mark'))
        elif status_filter == 'failed':
            test_attempts = test_attempts.filter(percentage__lt=F('test__pass_mark'))
        elif status_filter == 'pending':
            test_attempts = test_attempts.filter(feedback__isnull=True)

    # Handle feedback submission
    if request.method == 'POST' and (request.user.role == 'teacher' or request.user.is_superuser):
        test_attempt_id = request.POST.get('test_attempt_id')
        feedback_text = request.POST.get('feedback')
        
        if test_attempt_id and feedback_text:
            test_attempt = get_object_or_404(TestAttempt, id=test_attempt_id)
            feedback = Feedback.objects.create(
                test_attempt=test_attempt,
                teacher=request.user,
                feedback_text=feedback_text
            )
            messages.success(request, 'Feedback submitted successfully!')
            return redirect('performance_analytics:user_performance', user_id=user_id)

    # Pagination logic
    paginator = Paginator(test_attempts, 10)  # Show 10 attempts per page
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, show the first page.
        page_obj = paginator.get_page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page.
        page_obj = paginator.get_page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'user': user,
        'is_teacher': request.user.role == 'teacher' or request.user.is_superuser,
        'page_title': 'Test Results - MCQ Test System',
        'search_query': search_query,
        'filter_by': filter_by,
        'status_filter': status_filter,
    }

    return render(request, 'performance_analytics/user_performance.html', context)


@login_required
def test_details(request, test_attempt_id):
    # Fetch the TestAttempt object
    test_attempt = get_object_or_404(TestAttempt, id=test_attempt_id)
    
    # Check permissions
    if not (request.user.role == 'teacher' or request.user.is_superuser or request.user.id == test_attempt.user.id):
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    # Fetch feedback if available
    feedback = None
    if hasattr(test_attempt, 'feedback'):
        feedback = test_attempt.feedback

    # Calculate time taken
    if test_attempt.start_time and test_attempt.updated_at:
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

    # Calculate statistics
    test = test_attempt.test
    total_attempts = TestAttempt.objects.filter(test=test).count()
    
    if total_attempts > 0:
        # Calculate average percentage
        avg_percentage = TestAttempt.objects.filter(test=test).aggregate(avg=Avg('percentage'))['avg'] or 0
        avg_percentage = round(avg_percentage, 1)
        tests_with_feedback = TestAttempt.objects.filter(test=test, feedback__isnull=False).count()
    else:
        avg_percentage = 0
        tests_with_feedback = 0

    # Determine user perspective and role
    is_viewing_own_attempt = request.user.id == test_attempt.user.id
    is_teacher = request.user.role == 'teacher' or request.user.is_superuser
    is_student = request.user.role == 'student'

    # Determine the correct back URL based on user role
    if is_teacher:
        back_url = reverse('performance_analytics:visualize_performance', kwargs={'user_id': request.user.id})
        back_text = "Back to Class Overview"
    elif is_student and is_viewing_own_attempt:
        back_url = reverse('performance_analytics:user_performance', kwargs={'user_id': request.user.id})
        back_text = "Back to My Performance"
    else:
        # If a student is viewing another student's attempt (shouldn't happen due to permissions)
        return HttpResponseForbidden("You don't have permission to view this page.")

    context = {
        'test_attempt': test_attempt,
        'feedback': feedback,
        'total_attempts': total_attempts,
        'average_percentage': avg_percentage,
        'tests_with_feedback': tests_with_feedback,
        'time_taken': time_taken_str,
        'is_viewing_own_attempt': is_viewing_own_attempt,
        'is_teacher': is_teacher,
        'back_url': back_url,
        'back_text': back_text,
        'page_title': f'Test Details: {test_attempt.test.title}',
    }

    return render(request, 'performance_analytics/test_details.html', context)


@login_required
def create_feedback(request, test_attempt_id):
    # Fetch the TestAttempt object by ID
    test_attempt = get_object_or_404(TestAttempt, id=test_attempt_id)

    # Check if feedback already exists for this TestAttempt
    feedback = Feedback.objects.filter(test_attempt=test_attempt).first()

    if feedback:
        # If feedback exists, update it instead of creating a new one
        if request.method == 'POST':
            form = FeedbackForm(request.POST, instance=feedback)
            if form.is_valid():
                # Assign the teacher (current user) if it's missing
                feedback.teacher = request.user
                form.save()
                return redirect('performance_analytics:test_details', test_attempt_id=test_attempt.id)
        else:
            form = FeedbackForm(instance=feedback)
    else:
        # If no feedback exists, create new feedback
        if request.method == 'POST':
            form = FeedbackForm(request.POST)
            if form.is_valid():
                new_feedback = form.save(commit=False)
                new_feedback.test_attempt = test_attempt  # Associate with the TestAttempt
                new_feedback.teacher = request.user  # Assign teacher (current user)
                new_feedback.save()
                return redirect('performance_analytics:test_details', test_attempt_id=test_attempt.id)
        else:
            form = FeedbackForm()

    # Render the feedback creation page
    return render(request, 'performance_analytics/create_feedback.html', {'form': form, 'test_attempt': test_attempt, 'page_title': 'Create Feedback - MCQ Test System'})

@login_required
def update_feedback(request, test_attempt_id):
    # Fetch the TestAttempt and Feedback object
    test_attempt = get_object_or_404(TestAttempt, id=test_attempt_id)
    feedback = get_object_or_404(Feedback, test_attempt=test_attempt)

    # Check if the logged-in user is the teacher who provided the feedback
    if feedback.teacher != request.user:
        return redirect('performance_analytics:test_details', test_attempt_id=test_attempt.id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            return redirect('performance_analytics:test_details', test_attempt_id=test_attempt.id)
    else:
        form = FeedbackForm(instance=feedback)

    return render(request, 'performance_analytics/update_feedback.html', {'form': form, 'test_attempt': test_attempt, 'page_title': 'Update Feedback - MCQ Test System'})

@login_required
def delete_feedback(request, test_attempt_id):
    # Fetch the TestAttempt and Feedback object
    test_attempt = get_object_or_404(TestAttempt, id=test_attempt_id)
    feedback = get_object_or_404(Feedback, test_attempt=test_attempt)

    # Check if the logged-in user is the teacher who provided the feedback
    if feedback.teacher != request.user:
        return redirect('performance_analytics:test_details', test_attempt_id=test_attempt.id)

    # Handle deletion on POST request
    if request.method == 'POST':
        feedback.delete()
        return redirect('performance_analytics:test_details', test_attempt_id=test_attempt.id)

    return render(request, 'performance_analytics/delete_feedback.html', {'test_attempt': test_attempt, 'page_title': 'Delete Feedback- MCQ Test System'})

@login_required
def visualize_performance(request, user_id):
    if not (request.user.role == 'teacher' or request.user.is_superuser):
        return redirect('performance_analytics:student_analytics', student_id=request.user.id)
    
    students = get_user_model().objects.filter(role='student')
    student_performance = []
    
    # Prepare data for charts
    performance_data = []
    feedback_sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for student in students:
        attempts = TestAttempt.objects.filter(user=student)
        if attempts.exists():
            avg_percentage = attempts.aggregate(avg=Avg('percentage'))['avg'] or 0
            student_performance.append({
                'id': student.id,
                'name': student.username,
                'tests_taken': attempts.count(),
                'average_percentage': round(avg_percentage, 1)
            })
            
            # Collect performance data for line chart
            for attempt in attempts:
                performance_data.append({
                    'date': attempt.attempt_date.strftime('%Y-%m-%d'),
                    'percentage': attempt.percentage,
                    'student': student.username,
                    'test_name': attempt.test.title
                })
                
                # Count feedback sentiment
                if hasattr(attempt, 'feedback') and attempt.feedback and attempt.feedback.sentiment_label:
                    feedback_sentiment[attempt.feedback.sentiment_label] += 1

    # Create line chart for performance over time
    df = pd.DataFrame(performance_data) if performance_data else pd.DataFrame()
    if not df.empty:
        fig1 = px.line(df, x='date', y='percentage', color='student',
                      title='Student Performance Over Time',
                      labels={'date': 'Test Date', 'percentage': 'Score (%)', 'student': 'Student'},
                      template='simple_white')
        fig1.update_layout(height=400, margin=dict(t=30, b=30, l=30, r=30))
        performance_plot = fig1.to_html(full_html=False)
    else:
        performance_plot = ""

    # Create bar chart for average scores
    if student_performance:
        avg_scores = pd.DataFrame(student_performance)
        fig2 = px.bar(avg_scores, x='name', y='average_percentage',
                     title='Average Scores by Student',
                     labels={'name': 'Student', 'average_percentage': 'Average Score (%)'},
                     template='simple_white')
        fig2.update_layout(height=400, margin=dict(t=30, b=30, l=30, r=30))
        avg_scores_plot = fig2.to_html(full_html=False)
    else:
        avg_scores_plot = ""

    # Create pie chart for feedback sentiment
    if any(feedback_sentiment.values()):
        sentiment_data = pd.DataFrame({
            'sentiment': list(feedback_sentiment.keys()),
            'count': list(feedback_sentiment.values())
        })
        fig3 = px.pie(sentiment_data, values='count', names='sentiment',
                     title='Feedback Sentiment Distribution',
                     template='simple_white',
                     color='sentiment',
                     color_discrete_map={'positive': '#28a745', 'neutral': '#ffc107', 'negative': '#dc3545'})
        fig3.update_layout(height=400, margin=dict(t=30, b=30, l=30, r=30))
        sentiment_plot = fig3.to_html(full_html=False)
    else:
        sentiment_plot = ""

    summary_stats = {
        'total_students': len(student_performance),
        'class_average': round(sum(s['average_percentage'] for s in student_performance) / len(student_performance), 1) if student_performance else 0,
        'pass_rate': round(len([s for s in student_performance if s['average_percentage'] >= 70]) / len(student_performance) * 100, 1) if student_performance else 0,
        'total_tests': TestAttempt.objects.count()
    }

    context = {
        'student_performance': student_performance,
        'summary_stats': summary_stats,
        'performance_plot': performance_plot,
        'avg_scores_plot': avg_scores_plot,
        'sentiment_plot': sentiment_plot,
        'page_title': 'Performance Analytics Dashboard'
    }
    return render(request, 'performance_analytics/visualize_performance.html', context)

@login_required
def student_performance(request, user_id):
    if not (request.user.role == 'teacher' or request.user.is_superuser):
        return redirect('home')
    
    student = get_object_or_404(get_user_model(), id=user_id)
    test_attempts = TestAttempt.objects.filter(user=student).order_by('-attempt_date')
    
    return render(request, 'performance_analytics/user_performance.html', {
        'student': student,
        'test_attempts': test_attempts,
    })

@login_required
def visualize_student_performance(request, user_id):
    if not (request.user.role == 'teacher' or request.user.is_superuser):
        return redirect('home')
    
    # Similar to visualize_performance but for specific student
    # ... implementation similar to visualize_performance

@login_required
def student_analytics(request, student_id):
    # Get the student object
    student = get_object_or_404(get_user_model(), id=student_id)
    
    # Check authorization
    if not (request.user.role == 'teacher' or request.user.is_superuser or request.user.id == student_id):
        return redirect('home')
    
    # Get test attempts
    test_attempts = TestAttempt.objects.filter(user_id=student_id).order_by('-attempt_date')
    
    # Prepare performance data
    performance_data = []
    feedback_sentiment = {'positive': 0, 'neutral': 0, 'negative': 0}
    
    for attempt in test_attempts:
        performance_data.append({
            'date': attempt.attempt_date.strftime('%Y-%m-%d'),
            'percentage': attempt.percentage,
            'test_name': attempt.test.title,
            'attempt_id': attempt.id,
            'category': getattr(attempt.test, 'category', 'Uncategorized'),
            'pass_mark': attempt.test.pass_mark
        })
        
        # Count feedback sentiment
        if hasattr(attempt, 'feedback') and attempt.feedback and attempt.feedback.sentiment_label:
            feedback_sentiment[attempt.feedback.sentiment_label] += 1

    # Convert to DataFrame for analysis
    df = pd.DataFrame(performance_data) if performance_data else pd.DataFrame()
    
    # Create line chart for performance over time
    if not df.empty:
        fig1 = px.line(df, x='date', y='percentage', 
                      title='Score Progress',
                      labels={'date': 'Test Date', 'percentage': 'Score (%)'},
                      template='simple_white')
        fig1.update_layout(showlegend=False, height=400, margin=dict(t=30, b=30, l=30, r=30))
        timeline_plot = fig1.to_html(full_html=False)
        
        # Create bar chart for performance by category
        avg_by_category = df.groupby('category')['percentage'].mean().reset_index()
        fig2 = px.bar(avg_by_category, x='category', y='percentage',
                     title='Average Score by Subject',
                     labels={'category': 'Subject', 'percentage': 'Average Score (%)'},
                     template='simple_white')
        fig2.update_layout(height=400, margin=dict(t=30, b=30, l=30, r=30))
        avg_scores_plot = fig2.to_html(full_html=False)
        
        # Create pie chart for feedback sentiment
        if any(feedback_sentiment.values()):
            sentiment_data = pd.DataFrame({
                'sentiment': list(feedback_sentiment.keys()),
                'count': list(feedback_sentiment.values())
            })
            fig3 = px.pie(sentiment_data, values='count', names='sentiment',
                         title='Feedback Sentiment Distribution',
                         template='simple_white',
                         color='sentiment',
                         color_discrete_map={'positive': '#28a745', 'neutral': '#ffc107', 'negative': '#dc3545'})
            fig3.update_layout(height=400, margin=dict(t=30, b=30, l=30, r=30))
            sentiment_plot = fig3.to_html(full_html=False)
        else:
            sentiment_plot = ""
    else:
        timeline_plot = ""
        avg_scores_plot = ""
        sentiment_plot = ""

    # Calculate summary statistics
    summary_stats = {
        'total_attempts': len(df) if not df.empty else 0,
        'avg_score': round(df['percentage'].mean(), 1) if not df.empty else 0,
        'highest_score': int(df['percentage'].max()) if not df.empty else 0,
        'latest_score': int(df['percentage'].iloc[0]) if not df.empty else 0
    }

    # Determine user role and appropriate back URL
    is_teacher = request.user.role == 'teacher' or request.user.is_superuser
    is_viewing_own_analytics = request.user.id == student_id

    if is_teacher:
        back_url = reverse('performance_analytics:visualize_performance', kwargs={'user_id': request.user.id})
        back_text = "Back to Class Overview"
    elif is_viewing_own_analytics:
        back_url = reverse('performance_analytics:user_performance', kwargs={'user_id': request.user.id})
        back_text = "Back to My Performance"
    else:
        # This shouldn't happen due to permission checks above
        return HttpResponseForbidden("You don't have permission to view this page.")

    context = {
        'student': student,
        'timeline_plot': timeline_plot,
        'avg_scores_plot': avg_scores_plot,
        'sentiment_plot': sentiment_plot,
        'summary_stats': summary_stats,
        'performance_data': performance_data,
        'page_title': f'Analytics for {student.username}',
        'is_teacher': is_teacher,
        'back_url': back_url,
        'back_text': back_text
    }

    return render(request, 'performance_analytics/students_analytics.html', context)
