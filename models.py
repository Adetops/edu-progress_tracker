from config import Config
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from flask import jsonify, flash, render_template
import phonenumbers
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Database:
    def __init__(self):
        self.client = Config.get_client()
        self.db = self.client[Config.DB]
        
        self.db.users.create_index('email', unique=True)
        self.db.students.create_index('email', unique=True)

    
    # Students collection
    def new_student(self, name, email, phone_number, create_account=False, password=None):
        """Add new student and optionally create a user account"""
        # Validations
        if not name or not name.strip():
            raise ValueError("Name is required!")
        
        if not email or not email.strip():
            raise ValueError("Email is required!")
        if '@' not in email:
            raise ValueError("Invalid email format")
        
        # check for duplicate email
        existing = self.db.students.find_one({'email': email.lower()})
        if existing:
            raise ValueError("A student with this email already exists.")

        try:
            parsed = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number.")
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")
        
        student = {
            'name': name.strip(),
            'email': email.strip().lower(),
            'phone_number': phone_number,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = self.db.students.insert_one(student)
        student_id = str(result.inserted_id)
        
        # Create user account if requested
        if create_account and password:
            try:
                user_id = self.create_user(email, password, name, role='student')
                self.link_student_to_user(user_id, student_id)
            except ValueError as e:
                flash(str(e), 'danger')
                return render_template('add_student.html')
        
        return student_id
    
    
    # Retrieve list of all students
    def get_all_students(self):
        students = list(self.db.students.find())
        for student in students:
            student['_id'] = str(student['_id'])
        return students
    
    
    # Retrieve details of a student
    def get_student(self, student_id):
        student = self.db.students.find_one({'_id': ObjectId(student_id)})
        if not student:
            return jsonify({'error': f"Student {student_id} not found"})
        
        student['_id'] = str(student['_id'])
        return student
    
    
    # Courses collection
    def add_course(self, title, description, topics=None):
        if not title or not title.strip():
            raise ValueError("Course title is required")
        if not description or not description.strip():
            raise ValueError("Course description is required")
        
        course = {
            'title': title,
            'description': description,
            'topics': topics or [],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = self.db.courses.insert_one(course)
        return str(result.inserted_id)
    
    
    # Retrieve the list of all courses
    def get_all_courses(self):
        courses = list(self.db.courses.find())
        for course in courses:
            course['_id'] = str(course['_id'])
        return courses
    
    
    # Retrieve a specific course
    def get_course(self, course_id):
        course = self.db.courses.find_one({'_id': ObjectId(course_id)})
        if not course:
            return jsonify({"error": f"course {course['title']} not found"})
        
        course['_id'] = str(course['_id'])
        return course
    
    
    # Activities collection
    def log_activity(self, student_id, course_id, activity_type, topic, score=None, notes=None):
        activity = {
            'student_id': student_id,
            'course_id': course_id,
            'activity_type': activity_type, # 'assignment', 'quiz', 'lesson', etc.
            'topic': topic,
            'score': score,
            'notes': notes,
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = self.db.activities.insert_one(activity)
        return str(result.inserted_id)
    
    
    # Check students activities
    def get_all_activities(self):
        activities = list(self.db.activities.find().sort('completed_at', -1))
        for activity in activities:
            activity['_id'] = str(activity['_id'])
        return activities
    
    
    # Check a specific student activity
    def get_student_activities(self, student_id, course_id=None):
        query = {'student_id': student_id}
        if course_id:
            query['course_id'] = course_id
        
        activities = list(self.db.activities.find(query).sort('completed_at', -1))
        for activity in activities:
            activity['_id'] = str(activity['_id'])
        return activities


    def get_student_progress_by_course(self, student_id):
        """Get progress breakdown by course for a student"""
        activities = self.get_student_activities(student_id)
        courses = self.get_all_courses()
        
        progress = []
        for course in courses:
            course_activities = [activity for activity in activities if activity['course_id'] == course['_id']]
            
            if not course_activities:
                continue
            
            scores = [activity['score'] for activity in course_activities if activity.get('score')]
            
            progress.append({
                'course_id': course['_id'],
                'course_title': course['title'],
                'total_activities': len(course_activities),
                'average_score': round(sum(scores) / len(scores), 1) if scores else None,
                'last_activity': course_activities[0]['completed_at'] if course_activities else None
            })
        return progress


    def get_course_progress(self, course_id):
        """Get all students' progress in a specific course"""
        students = self.get_all_students()
        course = self.get_course(course_id)
        
        if not course:
            return None
        
        progress = []
        for student in students:
            activities = [activity for activity in self.get_student_activities(student['_id']) if activity['course_id'] == course_id]
            
            if not activities:
                continue
            
            scores = [activity['score'] for activity in activities if activity.get('score')]
            
            # Calculate topic completion if course has topics
            topics_completed = set()
            if course.get('topics'):
                for activity in activities:
                    if activity['topic'] in course['topics']:
                        topics_completed.add(activity['topic'])
                
                completion_rate = (len(topics_completed) / len(course['topics']) * 100) if course['topics'] else 0
            else:
                completion_rate = None
            
            progress.append({
                'student_id': student['_id'],
                'student_name': student['name'],
                'total_activities': len(activities),
                'average_score': round(sum(scores) / len(scores), 1) if scores else None,
                'completion_rate': round(completion_rate, 1) if completion_rate else None,
                'last_activity': activities[0]['completed_at'] if activities else None
            })

        return {
            'course': course,
            'student_progress': progress
        }


    def get_dashboard_stats(self):
        """Get overall statistics for dashboard"""
        total_students = self.db.students.count_documents({})
        total_courses = self.db.courses.count_documents({})
        total_activities = self.db.activities.count_documents({})
        
        # Get activities from last 7 days
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        recent_activities = self.db.activities.count_documents({'completed_at': {'$gte': week_ago}})
        
        # Get average score across all activities
        pipeline = [
            {'$match': {'score': {'$exists': True, '$ne': None}}},
            {'$group': {'_id': None, 'average_score': {'$avg': '$score'}}}
        ]
        result = list(self.db.activities.aggregate(pipeline))
        average_score = round(result[0]['average_score'], 1) if result else 0
        
        return {
            'total_students': total_students,
            'total_courses': total_courses,
            'total_activities': total_activities,
            'recent_activities': recent_activities,
            'avg': average_score
        }


    # ==================== USER METHODS ====================
    
    def create_user(self, email, password, name, role='teacher'):
        """Create a new user account"""
        if not email or not password or not name:
            raise ValueError('All email, password, and name are required.')
        
        # Validate role
        valid_roles = ['teacher', 'student', 'parent', 'admin']
        if role not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        
        # Check if user exists
        existing = self.db.users.find_one({'email': email.lower()})
        if existing:
            raise ValueError('A user with this email already exists.')
        
        user = {
            'email': email.lower(),
            'password_hash': generate_password_hash(password),
            'name': name,
            'role': role,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'is_active': True,
            'student_id': None      # Will be set if role is a student
        }
        
        result = self.db.users.insert_one(user)
        return str(result.inserted_id)
    
    def get_user_by_email(self, email):
        """Get user by his/her email"""
        user = self.db.users.find_one({'email': email.lower()})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    def get_user_by_id(self, user_id):
        """ Get user by ID"""
        try:
            user = self.db.users.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                # Ensure is_active exists in the data
                if 'is_active' not in user:
                    user['is_active'] = True
            return user
        except Exception as e:
            print(f"Error in get_user_by_id: {e}")
            return None

    def verify_password(self, email, password):
        """Verify user password"""
        user = self.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None
    
    def update_user_password(self, user_id, new_password):
        """Update user password"""
        self.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password_hash': generate_password_hash(new_password)}}
        )
        
    def link_student_to_user(self, user_id, student_id):
        """Link a student profile to a user account"""
        self.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'student_id': student_id}}
        )
    
    def get_all_users(self):
        """Admin retrieve profile of all users"""
        users = list(self.db.users.find())
        for user in users:
            user['_id'] = str(user['_id'])
            user.pop('password_hash', None)
        return users
    
    
