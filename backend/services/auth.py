from backend.services.database import users
import hashlib
from datetime import datetime

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str) -> dict | None:
    if users.find_one({"username": username}):
        return None

    result = users.insert_one({
        "username": username,
        "password": hash_password(password),
        "created_at": datetime.utcnow()
    })
    return users.find_one({"_id": result.inserted_id})

def login_user(username: str, password: str) -> dict | None:
    user = users.find_one({"username": username})
    if not user:
        return None

    if user["password"] != hash_password(password):
        return None

    # Check if user has completed profile setup
    from backend.services.database import has_user_profile
    user["has_profile"] = has_user_profile(str(user["_id"]))
    
    return user

