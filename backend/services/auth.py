from backend.services.database import users
import hashlib
from datetime import datetime


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, password: str) -> dict:
    if users.find_one({"username": username}):
        return {"success": False, "message": "El usuario ya existe"}

    result = users.insert_one(
        {
            "username": username,
            "password": hash_password(password),
            "created_at": datetime.utcnow(),
        }
    )
    user = users.find_one({"_id": result.inserted_id})
    return {"success": True, "user": user, "message": "Usuario creado exitosamente"}


def login_user(username: str, password: str) -> dict:
    user = users.find_one({"username": username})
    if not user:
        return {"success": False, "message": "Usuario no encontrado"}

    if user["password"] != hash_password(password):
        return {"success": False, "message": "Contraseña incorrecta"}

    # Check if user has completed profile setup
    from backend.services.database import has_user_profile

    user["has_profile"] = has_user_profile(str(user["_id"]))

    return {"success": True, "user": user, "message": "Inicio de sesión exitoso"}
