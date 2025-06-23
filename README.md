**MCQ-Based Test System for Exam Preparation Using Python and Django**

Project Domain / Category: **Data Science / Web Application Development**

Introduction: Students preparing for exams often struggle with effective self-assessment methods. Traditional study techniques, such as reading notes and textbooks, do not provide interactive or personalized learning experiences. Similarly, teachers require a streamlined platform to create tailored tests for their students.

This project addresses these challenges by developing an MCQ-based exam preparation system using Python and Django. Teachers can create and customize tests from a question bank or automatically generate MCQs from input text. Students can take tests, receive instant feedback, and track their performance over time. The platform provides an adaptive learning environment that simulates real exam conditions.


**Features:**

User Roles:

Teachers:
- Create and manage tests.
- Manage the question bank (add, edit, delete questions).
- Generate MCQs from text input using NLP.
- Review student performance and provide feedback.

Students:
- Attempt tests created by teachers.
- Receive real-time feedback.
- Review correct answers and explanations.
- Track progress and performance over time.

Functional Modules:
- User Registration & Profile Management (Teachers & Students)
- Question Bank Management (Teacher)
- Test Creation & Customization (Teacher)
- Test Execution & Real-Time Evaluation (Student)
- Performance Tracking & Analytics (Student & Teacher)
- Automatic MCQ Generation from Text (Teacher)

Tools & Technologies:
- Backend: Python (Django)
- Database: MySQL
- Frontend: HTML, CSS, Bootstrap
- NLP Library: NLTK (For automatic MCQ generation)
- Data Visualization: Matplotlib, Plotly (For performance tracking analytics)

Installation & Setup:

Clone the Repository:
```
git clone https://github.com/zahidabbas12/FYP25
cd mcq-test-system
```

Create a Virtual Environment & Install Dependencies:
```
python -m venv virtualenv
source virtualenv/bin/activate  # Activate (Linux/macOS)
virtualenv\Scripts\activate  # Activate (Windows)
pip install -r requirements.txt
```

Set Up the Database:
```
python manage.py migrate
```

Create a Superuser (Admin Login):
```
python manage.py createsuperuser
```

Run the Django Development Server:
```
python manage.py runserver
```
Access the system at http://127.0.0.1:8000/

Project Structure:
```
mcq-test-system/
│── accounts/                # User authentication & profile management
│── attempt_test/            # Student test-taking module
│── create_test/             # Teacher's test creation module
│── mcqs_system/             # Main Django project settings
│── media/                   # Stores uploaded files (if any)
│── performance_analytics/   # Performance tracking and analytics
│── question_bank/           # Question management module
│── templates/               # HTML templates for frontend
│── manage.py                # Django project management script
│── requirements.txt         # Required dependencies
│── .gitignore               # Git ignore file
```

Contributing:
Contributions are welcome! If you'd like to improve the system, please fork the repository, make changes, and submit a pull request.

NOTE: I developed this project as my Final Year Project, also part of my learning journey in Django, and I’d love to get feedback from others. Feel free to reach out if you have any questions or suggestions!

