from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import UserCreate, UserLogin, TokenResponse, User
from app.utils.helpers import hash_password, verify_password, create_jwt, decode_jwt
import uuid
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

# In production, swap this for DynamoDB
_fake_users_db: dict = {}


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate):
    """Register a new user and return a JWT."""
    if payload.email in _fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    hashed = hash_password(payload.password)
    user = User(
        id=user_id,
        email=payload.email,
        full_name=payload.full_name,
        org_id=payload.org_id,
        role=payload.role,
        hashed_password=hashed,
        created_at=datetime.utcnow(),
    )
    _fake_users_db[payload.email] = user.dict()

    token = create_jwt({"sub": user_id, "org_id": payload.org_id, "role": payload.role})
    return TokenResponse(access_token=token, user_id=user_id, org_id=payload.org_id)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    """Authenticate and return a JWT."""
    user = _fake_users_db.get(payload.email)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt({"sub": user["id"], "org_id": user["org_id"], "role": user["role"]})
    return TokenResponse(access_token=token, user_id=user["id"], org_id=user["org_id"])


@router.get("/me", response_model=dict)
async def me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Return current user info from JWT."""
    payload = decode_jwt(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload
