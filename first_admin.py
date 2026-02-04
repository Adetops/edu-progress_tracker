from models import Database

db = Database()

# Create admin account
try:
    admin_id = db.create_user(
        email="admin@edutracker.com",  # Change this
        password="admin123",  # Change this!
        name="Admin User",
        role="admin"
    )
    print(f"✓ Admin account created successfully!")
    print(f"Email: admin@edutracker.com")
    print(f"Password: admin123")
    print(f"\n⚠️  IMPORTANT: Change this password immediately after first login!")
except ValueError as e:
    print(f"Error: {e}")
