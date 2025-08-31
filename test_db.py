import os
from sql
alchemy.orm import Session
from noob_coderss.app.database import SessionLocal, Base, engine
from noob_coderss.app.models import User

def test_db():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Add a new user
        new_user = User(username="testuser", email="testuser@example.com")
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Added user: {new_user.username}, {new_user.email}")

        # Fetch all users






        users = db.query(User).all()
        print("All users in database:")
        for user in users:
            print(f"- {user.id}: {user.username}, {user.email}")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
