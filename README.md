# Educational Progress Tracker

A web-based application for tutors and educators to track student progress across multiple courses.

## Features

- **Student Management**: Add and track multiple students
- **Course Management**: Create courses with topics and track completion
- **Activity Logging**: Record assignments, quizzes, tests, and lessons
- **Progress Tracking**: View detailed analytics and progress reports
- **Search**: Find students and courses quickly
- **Export**: Download student reports in Excel format
- **Auth**: Tutor or educator authentication before access to students' dashboard

## Tech Stack

- **Backend**: Python, Flask
- **Database**: MongoDB Atlas
- **Frontend**: Bootstrap 5, HTML/CSS
- **Charts**: (Optional - can add Chart.js)

## Setup Instructions

### Prerequisites
- Python 3.12+
- MongoDB Atlas account (free tier)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd edu-progress_tracker
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```
MONGO_URI=your_mongodb_connection_string
SECRET_KEY=your_secret_key
```

5. Run the application:
```bash
python app.py
```

6. Visit http://127.0.0.1:5000

### Optional: Seed Sample Data
```bash
python seed_data.py
```

## Usage

### Adding Students
1. Navigate to Students → Add Student
2. Enter student name, email, and phone number
3. Click "Add Student"

### Creating Courses
1. Navigate to Courses → Add Course
2. Enter title, description, and topics (comma-separated)
3. Click "Add Course"

### Logging Activities
1. Click "Log Activity" from dashboard or student page
2. Select student, course, and activity type
3. Enter topic and optional score
4. Click "Log Activity"

### Viewing Progress
- **Dashboard**: Overview of all students and recent activities
- **Student Detail**: Individual student progress and activity history
- **Course Detail**: All students' progress in a specific course

## Project Structure
```
edu-tracker/
├── app.py              # Main Flask application
├── models.py           # Database models and operations
├── config.py           # Configuration
├── routes.py           # Routes
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── templates/         # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── students.html
│   ├── student_detail.html
│   ├── courses.html
│   ├── course_detail.html
│   └── ...
└── static/            # CSS, JS, images
```

## Future Enhancements

- [ ] User authentication
- [ ] Email notifications
- [ ] Advanced analytics and charts
- [ ] Mobile app
- [ ] Bulk import/export
- [ ] Assignment deadlines and reminders

## License

MIT License - feel free to use for your own projects!

## Support

For questions or issues, please open an issue on GitHub.
