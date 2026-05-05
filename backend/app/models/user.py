from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Organization(BaseModel):
    id: Optional[str] = None
    name: str
    industry: str
    country: str
    employee_count: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    targets: Optional[dict] = {}      # e.g. {"2030_reduction_pct": 50}


class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    full_name: str
    org_id: str
    role: UserRole = UserRole.ANALYST
    created_at: datetime = Field(default_factory=datetime.utcnow)
    hashed_password: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    org_id: str
    password: str
    role: UserRole = UserRole.ANALYST


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    org_id: str
