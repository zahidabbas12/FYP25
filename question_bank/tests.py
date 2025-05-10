from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import MCQ

# Create your tests here.

class MCQTests(TestCase):
    def setUp(self):
        # Create a test user (teacher)
        self.teacher = get_user_model().objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            role='teacher'
        )

    def test_create_mcq(self):
        """Test creating a new MCQ"""
        mcq = MCQ.objects.create(
            teacher=self.teacher,
            question='What is 2+2?',
            option_a='3',
            option_b='4',
            option_c='5',
            option_d='6',
            correct_answer='B',
            category='Math',
            difficulty='Easy',
            explanation='Basic arithmetic'
        )
        
        self.assertEqual(mcq.question, 'What is 2+2?')
        self.assertEqual(mcq.correct_answer, 'B')
        self.assertEqual(mcq.category, 'Math')
        self.assertEqual(mcq.teacher, self.teacher)

    def test_mcq_str_representation(self):
        """Test the string representation of MCQ"""
        mcq = MCQ.objects.create(
            teacher=self.teacher,
            question='Test question?',
            option_a='A',
            option_b='B',
            option_c='C',
            option_d='D',
            correct_answer='A',
            category='Math',
            difficulty='Easy',
            explanation='Test explanation'
        )
        
        self.assertEqual(str(mcq), 'Test question?')
