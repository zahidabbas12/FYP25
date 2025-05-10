from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Test, TestMCQ
from question_bank.models import MCQ

class TestModelTests(TestCase):
    def setUp(self):
        # Create a test user (teacher)
        self.teacher = get_user_model().objects.create_user(
            username='testteacher',
            email='teacher@test.com',
            password='testpass123',
            role='teacher'
        )
        
        # Create a test MCQ
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

    def test_create_test(self):
        """Test creating a new test"""
        test = Test.objects.create(
            teacher=self.teacher,
            title='Test Title',
            description='Test Description',
            duration=30,
            pass_mark=60
        )
        
        self.assertEqual(test.title, 'Test Title')
        self.assertEqual(test.duration, 30)
        self.assertEqual(test.pass_mark, 60)
        self.assertFalse(test.is_published)
        self.assertTrue(test.is_active)

    def test_add_mcq_to_test(self):
        """Test adding an MCQ to a test"""
        test = Test.objects.create(
            teacher=self.teacher,
            title='Test Title',
            description='Test Description',
            duration=30,
            pass_mark=60
        )
        
        test_mcq = TestMCQ.objects.create(
            test=test,
            mcq=self.mcq,
            order=1
        )
        
        self.assertEqual(test_mcq.test, test)
        self.assertEqual(test_mcq.mcq, self.mcq)
        self.assertEqual(test_mcq.order, 1)
