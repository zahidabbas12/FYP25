from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_user_registration(self):
        """Test user registration functionality"""
        response = self.client.post(reverse('register'), {
            'username': 'newstudent',
            'email': 'newstudent@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': 'student'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration
        self.assertTrue(get_user_model().objects.filter(username='newstudent').exists())

    def test_user_login(self):
        """Test user login functionality"""
        # Test student login
        response = self.client.post(reverse('login'), {
            'username': 'teststudent',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login
        
        # Test teacher login
        response = self.client.post(reverse('login'), {
            'username': 'testteacher',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_dashboard_access(self):
        """Test dashboard access based on user role"""
        # Test teacher dashboard access
        self.client.login(username='testteacher', password='testpass123')
        response = self.client.get(reverse('teacher_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test student dashboard access
        self.client.login(username='teststudent', password='testpass123')
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Test student trying to access teacher dashboard
        response = self.client.get(reverse('teacher_dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_profile_operations(self):
        """Test profile view, edit, and delete operations"""
        self.client.login(username='teststudent', password='testpass123')
        
        # Test profile view
        response = self.client.get(reverse('profile_view'))
        self.assertEqual(response.status_code, 200)
        
        # Test profile edit
        response = self.client.post(reverse('profile_edit'), {
            'username': 'teststudent_updated',
            'email': 'updated@test.com'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful edit
        
        # Verify the changes
        user = get_user_model().objects.get(id=self.student.id)
        self.assertEqual(user.email, 'updated@test.com')
