from models import Database


db = Database()
print("✓ Connected to MongoDB!")

# Test adding a student
student_id = db.new_student("Test Student", "test@example.com", "+2348123456789")
print(f"✓ Created test student with ID: {student_id}")

# Test retrieving students
students = db.get_all_students()
print(f"✓ Found {len(students)} student(s)")

print("\nDatabase setup successful!")
