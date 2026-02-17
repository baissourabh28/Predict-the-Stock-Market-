"""
Reset test user with correct password
"""
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def reset_test_user():
    """Reset test user password"""
    db = SessionLocal()
    
    try:
        # Find test user
        user = db.query(User).filter(User.username == "testuser").first()
        
        if user:
            print(f"Found user: {user.username}")
            # Update password
            user.password_hash = get_password_hash("testpassword123")
            db.commit()
            print("✅ Password updated successfully!")
        else:
            print("Creating new test user...")
            user = User(
                username="testuser",
                email="testuser@example.com",
                password_hash=get_password_hash("testpassword123"),
                is_active=True
            )
            db.add(user)
            db.commit()
            print("✅ Test user created successfully!")
        
        print(f"\nTest User Credentials:")
        print(f"  Username: testuser")
        print(f"  Password: testpassword123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_test_user()
