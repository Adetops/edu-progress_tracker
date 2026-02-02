from models import Database
import random
from datetime import datetime, timedelta


db = Database()

# Add sample students
students = [
    ("Alice Johnson", "alice@example.com", "+234 8147895670"),
    ("Bob Smith", "bob@example.com", "+234 7031225678"),
    ("Carol Williams", "carol@example.com", "+1 2478677421"),
]

student_ids = []
for name, email, phone_number in students:
    sid = db.new_student(name, email, phone_number)
    student_ids.append(sid)
    print(f"Added student: {name}")

# Add sample courses
courses = [
    ("Algebra I", "Introduction to algebraic concepts", ["Variables", "Equations", "Graphing", "Functions"]),
    ("World History", "Survey of world history from ancient to modern times", ["Ancient Civilizations", "Middle Ages", "Renaissance", "Modern Era"]),
    ("Biology", "Introduction to biological sciences", ["Cells", "Genetics", "Evolution", "Ecosystems"]),
]

course_ids = []
for title, desc, topics in courses:
    cid = db.add_course(title, desc, topics)
    course_ids.append(cid)
    print(f"Added course: {title}")

# Add sample activities
activity_types = ["lesson", "assignment", "quiz", "test"]

for student_id in student_ids:
    for course_id in course_ids:
        # Add 3-8 random activities per student per course
        num_activities = random.randint(3, 8)
        for i in range(num_activities):
            activity_type = random.choice(activity_types)
            score = random.randint(60, 100) if activity_type in ["quiz", "test", "assignment"] else None
            
            # Get course to use its topics
            course = db.get_course(course_id)
            topic = random.choice(course['topics']) if course.get('topics') else f"Topic {i+1}"
            
            db.log_activity(
                student_id=student_id,
                course_id=course_id,
                activity_type=activity_type,
                topic=topic,
                score=score
            )

print("\n✓ Sample data created successfully!")
print(f"Students: {len(student_ids)}")
print(f"Courses: {len(course_ids)}")
print("Activities: Multiple per student/course")
