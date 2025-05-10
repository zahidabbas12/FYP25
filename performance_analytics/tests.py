from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from attempt_test.models import TestAttempt
from create_test.models import Test
from question_bank.models import MCQ
from .models import Feedback

class PerformanceAnalyticsTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.teacher = get_user_model().objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            role='teacher'
        )
        self.student = get_user_model().objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            role='student'
        )
        
        # Create a test
        self.test = Test.objects.create(
            teacher=self.teacher,
            title='Test Title',
            description='Test Description',
            duration=30,
            pass_mark=60,
            is_published=True
        )
        
        # Create a test attempt
        self.test_attempt = TestAttempt.objects.create(
            user=self.student,
            test=self.test,
            score=80,
            percentage=80.0,
            start_time=timezone.now(),
            is_completed=True
        )

    def test_user_performance_view(self):
        """Test user performance view access"""
        # Login as teacher
        self.client.login(username='testteacher', password='testpass123')
        
        # Test accessing student's performance
        response = self.client.get(reverse('performance_analytics:user_performance', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        
        # Test student accessing own performance
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('performance_analytics:user_performance', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)

    def test_test_details_view(self):
        """Test test details view access"""
        # Login as teacher
        self.client.login(username='testteacher', password='testpass123')
        
        # Test accessing test details
        response = self.client.get(reverse('performance_analytics:test_details', args=[self.test_attempt.id]))
        self.assertEqual(response.status_code, 200)

    def test_feedback_operations(self):
        """Test feedback creation, update, and deletion"""
        # Login as teacher
        self.client.login(username='testteacher', password='testpass123')
        
        # Test creating feedback
        response = self.client.post(reverse('performance_analytics:create_feedback', args=[self.test_attempt.id]), {
            'content': 'Good work!',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        
        # Verify feedback was created
        feedback = Feedback.objects.filter(test_attempt=self.test_attempt).first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.content, 'Good work!')
        
        # Test updating feedback
        response = self.client.post(reverse('performance_analytics:update_feedback', args=[self.test_attempt.id]), {
            'content': 'Excellent work!',
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful update
        
        # Verify feedback was updated
        feedback.refresh_from_db()
        self.assertEqual(feedback.content, 'Excellent work!')

    def test_analytics_visualization(self):
        """Test analytics visualization views"""
        # Login as teacher
        self.client.login(username='testteacher', password='testpass123')
        
        # Test accessing class performance visualization
        response = self.client.get(reverse('performance_analytics:visualize_performance', args=[self.teacher.id]))
        self.assertEqual(response.status_code, 200)
        
        # Test accessing student analytics
        response = self.client.get(reverse('performance_analytics:student_analytics', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        
        # Verify student can access their own analytics
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('performance_analytics:student_analytics', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
