from flask_login import UserMixin
from models import Database

class User(UserMixin):
    """User class for Flask-Login"""
    
    def __init__(self, user_data):
        self.id = user_data['_id']
        self.email = user_data['email']
        self.name = user_data['name']
        self.role = user_data['role']
        self._is_active = user_data.get('is_active', True)
        self.student_id = user_data.get('student_id')
    
    
    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        self._is_active = value
    
    def get_id(self):
        return str(self.id)
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_student(self):
        return self.role == 'student'
    
    def is_parent(self):
        return self.role == 'parent'
    
    def is_admin(self):
        return self.role == 'admin'
    
    @staticmethod
    def get(user_id):
        """Load user by ID"""
        db = Database()
        user_data = db.get_user_by_id(user_id)
        if user_data:
            return User(user_data)
        return None
