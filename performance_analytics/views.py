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
from django.db.models import Avg, Count
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


# try:
#     nltk.data.find('vader_lexicon')
# except LookupError:
#     nltk.download('vader_lexicon')


@login_required
def user_performance(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    print(f"Viewing performance for user: {user.username} (ID: {user_id})")
    print(f"Current user: {request.user.username} (Role: {request.user.role})")
    
    # Check permissions and get appropriate test attempts
    if request.user.role == 'teacher' or request.user.is_superuser:
        # For teachers, show attempts for tests they created
        test_attempts = TestAttempt.objects.filter(
            test__teacher=request.user
        ).select_related('test', 'user', 'feedback')
        print(f"Teacher view - Found {test_attempts.count()} attempts")
    elif request.user.id == user_id:
        # For students, show their own attempts
        test_attempts = TestAttempt.objects.filter(
            user=user
        ).select_related('test', 'user', 'feedback')
        print(f"Student view - Found {test_attempts.count()} attempts")
    else:
        return HttpResponseForbidden("You don't have permission to view this page.")

    # Pagination logic
    paginator = Paginator(test_attempts, 10)  # Show 5 attempts per page
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
        'page_obj': page_obj,  # Pass the page_obj to template for pagination
        'user': user,
        'page_title': 'User Performance - MCQ Test System'
    }

    return render(request, 'performance_analytics/user_performance.html', context)

    return render(request, 'performance_analytics/user_performance.html', context)


@login_required
def test_details(request, test_attempt_id):
    # Fetch the TestAttempt object by the provided test_attempt_id.
    test_attempt = get_object_or_404(TestAttempt, id=test_attempt_id)
    
    # Fetch feedback if available
    feedback = None
    if hasattr(test_attempt, 'feedback'):
        feedback = test_attempt.feedback

    # Check if the user has permission to view the details
    if request.user.role == 'teacher' or request.user.is_superuser:
        # For teachers, display additional information
        teacher_feedback = feedback if feedback else None
    elif request.user.id == test_attempt.user.id:
        # For students, display only their attempt details
        teacher_feedback = feedback if feedback else None
    else:
        return HttpResponseForbidden("You don't have permission to view this page.")
    
    # Calculate statistics for the test (if it's available)
    test = test_attempt.test  # Get the associated test for the test attempt
    total_attempts = TestAttempt.objects.filter(test=test).count()  # Count all attempts for this test

    if total_attempts > 0:
        average_score = sum(attempt.score for attempt in TestAttempt.objects.filter(test=test)) / total_attempts
        
        # Count the number of tests with feedback (based on the original queryset)
        tests_with_feedback = TestAttempt.objects.filter(test=test, feedback__isnull=False).count()
    else:
        average_score = 0
        tests_with_feedback = 0
    
    # Add the calculated statistics to the context
    context = {
        'test_attempt': test_attempt,
        'feedback': feedback,
        'teacher_feedback': teacher_feedback,  # Including feedback if teacher or student
        'user': request.user,
        'average_score': round(average_score, 1),  # Rounded average score
        'tests_with_feedback': tests_with_feedback,
        'total_attempts': total_attempts,
        'page_title': 'Test Details - MCQ Test System',
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
    # Initialize sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    
    # Fetch test attempts based on user role
    if request.user.role == 'teacher' or request.user.is_superuser:
        test_attempts = TestAttempt.objects.filter(test__teacher=request.user)
    elif request.user.role == 'student' and request.user.id == user_id:
        test_attempts = TestAttempt.objects.filter(user_id=user_id)
    else:
        test_attempts = []

    # Prepare performance metrics
    performance_data = []
    
    for attempt in test_attempts:
        # Calculate time taken for each test attempt (assuming you have start_time and updated_at)
        if attempt.start_time and attempt.updated_at:
            time_taken = attempt.updated_at - attempt.start_time
            total_seconds = int(time_taken.total_seconds())
            
            # Calculate hours, minutes, and seconds
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            time_taken_str = f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''} {seconds} second{'s' if seconds != 1 else ''}"
        else:
            time_taken_str = "N/A"  # If time data is missing

        # Get feedback sentiment
        feedback = getattr(attempt, 'feedback', None)
        sentiment_score = sia.polarity_scores(feedback.content) if feedback and feedback.content else {
            'pos': 0, 'neu': 0, 'neg': 0, 'compound': 0
        }

        # Append performance data
        performance_data.append({
            'date': attempt.attempt_date.strftime('%Y-%m-%d'),
            'score': attempt.score,
            'test_name': attempt.test.title,
            'student': attempt.user.username,
            'student_id': attempt.user.id,
            'sentiment_score': sentiment_score['compound'],
            'sentiment': get_sentiment_label(sentiment_score['compound']),
            'time_taken': time_taken_str,  
            
        })

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(performance_data)
    
    # Generate visualizations
    if not df.empty:
        # 1. Score Timeline
        fig1 = px.line(df, x='date', y='score', color='student', title='Score Progress Over Time')
        timeline_plot = fig1.to_html(full_html=False)

        # 2. Average Scores by Test
        avg_scores = df.groupby('test_name')['score'].mean().reset_index()
        fig2 = px.bar(avg_scores, x='test_name', y='score', title='Average Scores by Test')
        avg_scores_plot = fig2.to_html(full_html=False)

        # 3. Sentiment vs Score Correlation
        df['sentiment_label'] = df['sentiment'].apply(lambda x: x['label'])
        fig3 = px.scatter(df, 
                         x='sentiment_score', 
                         y='score',
                         color='sentiment_label',
                         title='Feedback Sentiment vs Score Correlation',
                         labels={'sentiment_score': 'Sentiment (Negative → Positive)', 'score': 'Test Score (%)'})
        sentiment_plot = fig3.to_html(full_html=False)

        # 4. Performance Distribution
        fig4 = px.histogram(df, x='score', nbins=20, title='Score Distribution')
        distribution_plot = fig4.to_html(full_html=False)

    else:
        timeline_plot = ""
        avg_scores_plot = ""
        sentiment_plot = ""
        distribution_plot = ""

    # Calculate summary statistics
    summary_stats = {
        'total_attempts': len(df) if not df.empty else 0,
        'avg_score': df['score'].mean() if not df.empty else 0,
        'highest_score': df['score'].max() if not df.empty else 0,
        'lowest_score': df['score'].min() if not df.empty else 0,
    }

    context = {
        'timeline_plot': timeline_plot,
        'avg_scores_plot': avg_scores_plot,
        'sentiment_plot': sentiment_plot,
        'distribution_plot': distribution_plot,
        'summary_stats': summary_stats,
        'performance_data': performance_data,
        'page_title': 'Performance Analytics - MCQ Test System'
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
    # Check if user is authorized
    if not (request.user.role == 'teacher' or request.user.is_superuser):
        return redirect('home')
    
    # Get student object
    student = get_object_or_404(get_user_model(), id=student_id)
    
    # Initialize sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    
    # Fetch all test attempts for this student
    test_attempts = TestAttempt.objects.filter(user_id=student_id)
    
    # Prepare performance metrics
    performance_data = []
    
    for attempt in test_attempts:
        # Get feedback sentiment
        feedback = getattr(attempt, 'feedback', None)
        sentiment_score = sia.polarity_scores(feedback.content) if feedback and feedback.content else {
            'pos': 0, 'neu': 0, 'neg': 0, 'compound': 0
        }
        
        # Append performance data
        performance_data.append({
            'date': attempt.attempt_date.strftime('%Y-%m-%d'),
            'score': attempt.score,
            'test_name': attempt.test.title,
            'student': attempt.user.username,
            'student_id': attempt.user.id,
            'sentiment_score': sentiment_score['compound'],
            'sentiment': get_sentiment_label(sentiment_score['compound'])
        })

    # Convert to DataFrame for analysis
    df = pd.DataFrame(performance_data)
    
    if not df.empty:
        # 1. Score Timeline
        fig1 = px.line(df, x='date', y='score',
                      title=f'Score Progress Over Time - {student.username}')
        timeline_plot = fig1.to_html(full_html=False)

        # 2. Average Scores by Test
        avg_scores = df.groupby('test_name')['score'].mean().reset_index()
        fig2 = px.bar(avg_scores, x='test_name', y='score',
                     title=f'Average Scores by Test - {student.username}')
        avg_scores_plot = fig2.to_html(full_html=False)

        # 3. Sentiment vs Score Correlation
        df['sentiment_label'] = df['sentiment'].apply(lambda x: x['label'])
        fig3 = px.scatter(df, 
                         x='sentiment_score', 
                         y='score',
                         color='sentiment_label',
                         title='Feedback Sentiment vs Score Correlation',
                         labels={
                             'sentiment_score': 'Sentiment (Negative → Positive)',
                             'score': 'Test Score (%)',
                             'sentiment_label': 'Sentiment Category'
                         })
        sentiment_plot = fig3.to_html(full_html=False)

        # 4. Performance Distribution
        fig4 = px.histogram(df, x='score', nbins=20,
                          title=f'Score Distribution - {student.username}')
        distribution_plot = fig4.to_html(full_html=False)
    else:
        timeline_plot = ""
        avg_scores_plot = ""
        sentiment_plot = ""
        distribution_plot = ""

    # Calculate summary statistics
    summary_stats = {
        'total_attempts': len(df) if not df.empty else 0,
        'avg_score': df['score'].mean() if not df.empty else 0,
        'highest_score': df['score'].max() if not df.empty else 0,
        'lowest_score': df['score'].min() if not df.empty else 0,
    }

    context = {
        'student': student,
        'timeline_plot': timeline_plot,
        'avg_scores_plot': avg_scores_plot,
        'sentiment_plot': sentiment_plot,
        'distribution_plot': distribution_plot,
        'summary_stats': summary_stats,
        'performance_data': performance_data,
        'page_title': 'Performance Analytics - MCQ Test System'
    }

    return render(request, 'performance_analytics/students_analytics.html', context)

def get_sentiment_label(compound_score):
    """Convert compound sentiment score to a human-readable label"""
    if compound_score >= 0.05:
        return {'label': 'Positive', 'class': 'text-success'}
    elif compound_score <= -0.05:
        return {'label': 'Negative', 'class': 'text-danger'}
    else:
        return {'label': 'Neutral', 'class': 'text-warning'}
