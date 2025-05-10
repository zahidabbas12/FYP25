from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from create_test.models import Test, TestMCQ
from question_bank.models import MCQ
from .models import TestAttempt, QuestionAttempt

class TestAttemptTests(TestCase):
    def setUp(self):
        # Create a test user (student)
        self.student = get_user_model().objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            role='student'
        )
        
        # Create a test user (teacher)
        self.teacher = get_user_model().objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            role='teacher'
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
        
        # Create an MCQ
        self.mcq = MCQ.objects.create(
            teacher=self.teacher,
            question='Test question?',
            option_a='Option A',
            option_b='Option B',
            option_c='Option C',
            option_d='Option D',
            correct_answer='A',
            category='Math',
            difficulty='Easy',
            explanation='Test explanation'
        )
        
        # Add MCQ to test
        self.test_mcq = TestMCQ.objects.create(
            test=self.test,
            mcq=self.mcq,
            order=1
        )

    def test_create_test_attempt(self):
        """Test creating a new test attempt"""
        test_attempt = TestAttempt.objects.create(
            user=self.student,
            test=self.test,
            start_time=timezone.now()
        )
        
        self.assertEqual(test_attempt.user, self.student)
        self.assertEqual(test_attempt.test, self.test)
        self.assertFalse(test_attempt.is_completed)
        self.assertIsNotNone(test_attempt.start_time)

    def test_question_attempt(self):
        """Test creating a question attempt"""
        test_attempt = TestAttempt.objects.create(
            user=self.student,
            test=self.test,
            start_time=timezone.now()
        )
        
        # Get the correct answer text
        correct_answer_text = getattr(self.mcq, f'option_{self.mcq.correct_answer.lower()}')
        selected_answer_text = getattr(self.mcq, f'option_a')  # We're selecting option A which is correct
        
        question_attempt = QuestionAttempt.objects.create(
            test_attempt=test_attempt,
            question=self.mcq,
            selected_option='A',  # Correct answer
            is_correct=(selected_answer_text == correct_answer_text)
        )
        
        self.assertEqual(question_attempt.test_attempt, test_attempt)
        self.assertEqual(question_attempt.question, self.mcq)
        self.assertEqual(question_attempt.selected_option, 'A')
        self.assertTrue(question_attempt.is_correct)
