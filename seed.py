from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def seed_users():
    db = SessionLocal()
    user1 = User(username="alice", hashed_password=get_password_hash("password1"))
    user2 = User(username="bob", hashed_password=get_password_hash("password2"))

    db.add(user1)
    db.add(user2)
    db.commit()

if __name__ == "__main__":
    seed_users()

