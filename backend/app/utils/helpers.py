import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_jwt(payload: dict, expires_hours: int = JWT_EXPIRY_HOURS) -> str:
    data = payload.copy()
    data["exp"] = datetime.utcnow() + timedelta(hours=expires_hours)
    data["iat"] = datetime.utcnow()
    return jwt.encode(data, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def kg_to_tonnes(kg: float) -> float:
    return round(kg / 1000, 4)


def format_co2e(kg: float) -> str:
    if kg >= 1_000_000:
        return f"{kg/1_000_000:.2f} kt CO2e"
    if kg >= 1000:
        return f"{kg/1000:.2f} t CO2e"
    return f"{kg:.1f} kg CO2e"
