from flask import Blueprint, render_template, send_file, request, redirect, url_for, flash, jsonify
from models import Database
from config import Config
from datetime import datetime, timezone
import openpyxl
from openpyxl.styles import Font, Alignment
from io import BytesIO


bp = Blueprint('main', __name__)
db = Database()

# Home route
@bp.route('/')
def index():
    stats = db.get_dashboard_stats()
    students = db.get_all_students()
    courses = db.get_all_courses()
    recent_activities = db.get_all_activities()[:10]
    return render_template('index.html',
                           stats=stats,
                           students=students,
                           courses=courses,
                           recent_activities=recent_activities)


# Student routes
@bp.route('/students')
def students_list():
    students = db.get_all_students()
    return render_template('students.html', students=students)

@bp.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            
            db.new_student(name, email, phone_number)
            flash(f'Student {name} added successfully!', 'success')
            return redirect(url_for('students_list'))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('add_student.html')
        except Exception as e:
            flash('An error occurred. Please try again.', 'danger')
            return render_template('add_student.html')
    
    return render_template('add_student.html')

@bp.route('/students/<student_id>')
def student_detail(student_id):
    student = db.get_student(student_id)
    
    if not student:
        flash('Student not found', 'danger')
        return redirect(url_for('students_list'))
    
    activities = db.get_student_activities(student_id)
    course_progress = db.get_student_progress_by_course(student_id)
    
    # Calculate progress statistics
    total_activities = len(activities)
    quiz_scores = [activity['score'] for activity in activities if activity.get('score')]
    average_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
    
    return render_template('student_detail.html',
                           student=student,
                           activities=activities,
                           course_progress=course_progress,
                           total_activities=total_activities,
                           average_score=round(average_score, 1))
    
# Courses routes
@bp.route('/courses')
def courses_list():
    courses = db.get_all_courses()
    return render_template('courses.html', courses=courses)

@bp.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            topics_raw = request.form.get('topics', '')
            topics = [topic.strip() for topic in topics_raw.split(',') if topic.strip()]
            
            db.add_course(title, description, topics)
            flash(f'You have successfully registered for {title} course!', 'success')
            return redirect(url_for(courses_list))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('add_course.html')
        except Exception as e:
            flash('An error occurred. Please try again.', 'danger')
            return render_template('add_course.html')

    return render_template('add_course.html')


@bp.route('/courses/<course_id>')
def course_detail(course_id):
    progress_data = db.get_course_progress(course_id)
    
    if not progress_data:
        flash('Course not found', 'danger')
        return redirect(url_for('courses_list'))
    
    return render_template('course_detail.html', 
                         course=progress_data['course'],
                         student_progress=progress_data['student_progress'])



# Activity routes
@bp.route('/activities/log', methods=['GET', 'POST'])
def log_activity():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        course_id = request.form.get('course_id')
        activity_type = request.form.get('activity_type')
        topic = request.form.get('topic')
        score = request.form.get('score')
        notes = request.form.get('notes')
        
        # Convert score to int if provided
        score = int(score) if score else None
        
        db.log_activity(student_id, course_id, activity_type, topic, score, notes)
        flash('Activity successfully logged', 'success')
        return redirect(url_for('index'))
    
    students = db.get_all_students()
    courses = db.get_all_courses()
    return render_template('log_activity.html', students=students, courses=courses)

# Search query handler
@bp.route('/search')
def search():
    query = request.args.get('q', '').strip()
    
    if not query:
        return redirect(url_for('index'))
    
    # Search students
    students = db.db.students.find({
        '$or': [
            {'name': {'$regex': query, '$options': 'i'}},
            {'email': {'$regex': query, '$options': 'i'}}
        ]
    })
    students = list(students)
    for s in students:
        s['_id'] = str(s['_id'])
    
    # Search courses
    courses = db.db.courses.find({
        '$or': [
            {'title': {'$regex': query, '$options': 'i'}},
            {'description': {'$regex': query, '$options': 'i'}}
        ]
    })
    courses = list(courses)
    for c in courses:
        c['_id'] = str(c['_id'])
    
    return render_template('search_results.html', 
                         query=query, 
                         students=students, 
                         courses=courses)


# Export students' report
@bp.route('/export/student/<student_id>')
def export_student_report(student_id):
    student = db.get_student(student_id)
    activities = db.get_student_activities(student_id)
    
    if not student:
        flash(f'Student {student_id} not found', 'danger')
        return redirect(url_for('students_list'))
    
    # Creating workbook
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Student Report"
    
    # Header
    worksheet['A1'] = f"Progress Report: {student['name']}"
    worksheet['A1'].font = Font(size=14, bold=True)
    worksheet['A2'] = f"Email: {student['email']}"
    worksheet['A3'] = f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
    
    # Activity table headers
    worksheet['A5'] = "Date"
    worksheet['B5'] = "Course"
    worksheet['C5'] = "Type"
    worksheet['D5'] = "Topic"
    worksheet['E5'] = "Score"
    worksheet['F5'] = "Notes"
    
    for cell in ['A5', 'B5', 'C5', 'D5', 'E5', 'F5']:
        worksheet[cell].font = Font(bold=True)
    
    # Activities
    row = 6
    for activity in activities:
        course = db.get_course(activity['course_id'])
        worksheet[f'A{row}'] = activity['completed_at']
        worksheet[f'B{row}'] = course['title'] if course else 'Unknown'
        worksheet[f'C{row}'] = activity['activity_type']
        worksheet[f'D{row}'] = activity['topic']
        worksheet[f'E{row}'] = activity.get('score', '-')
        worksheet[f'F{row}'] = activity.get('notes', '')
        row += 1
    
    # Adjust column widths
    worksheet.column_dimensions['A'].width = 12
    worksheet.column_dimensions['B'].width = 20
    worksheet.column_dimensions['C'].width = 12
    worksheet.column_dimensions['D'].width = 25
    worksheet.column_dimensions['E'].width = 8
    worksheet.column_dimensions['F'].width = 30
    
    # Save to BytesIO
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"{student['name']}_report.xlsx"
    )
