import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI no está definido en el .env")

client = MongoClient(MONGO_URI)

db = client.get_database()


users = db["users"]
user_profiles = db["user_profiles"]
daily_states = db["daily_states"]


def check_connection():
    try:
        client.admin.command("ping")
        return True
    except Exception as e:
        print("Error MongoDB:", e)
        return False


def save_user_profile(profile: dict):
    return user_profiles.insert_one(profile)


def get_user_profile(user_id: str):
    """Get user profile by user_id field"""
    return user_profiles.find_one({"user_id": user_id})


def has_user_profile(user_id: str) -> bool:
    """Check if user has completed profile setup"""
    return user_profiles.find_one({"user_id": user_id}) is not None


def update_user_profile(user_id: str, updates: dict):
    """Update user profile with new data"""
    result = user_profiles.update_one({"user_id": user_id}, {"$set": updates})
    return result.modified_count > 0
