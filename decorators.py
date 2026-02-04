from flask import Flask, redirect, url_for, flash
from flask_login import LoginManager, current_user
from functools import wraps
from auth import User

# ==================== DECORATORS ====================

def teacher_required(f):
    """Decorator to require teacher role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        if not (current_user.is_teacher() or current_user.is_admin()):
            flash('You need teacher privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))
        if not current_user.is_admin():
            flash('You need administrator privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
