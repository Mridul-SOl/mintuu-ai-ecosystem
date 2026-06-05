"""
Mintuu AI Ecosystem — Auth API Routes
=======================================
Signup, login, token refresh, account management.
"""
import logging
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field, EmailStr

from mintuu_ai_ecosystem.api.auth import (
    UserManager, create_access_token, create_refresh_token, decode_token,
)

logger = logging.getLogger("mintuu.auth.routes")

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Global reference — set during app startup
_user_manager: Optional[UserManager] = None


def set_user_manager(um: UserManager):
    global _user_manager
    _user_manager = um


def get_user_manager() -> UserManager:
    if not _user_manager:
        raise HTTPException(503, "Auth system not initialized")
    return _user_manager


# ============================================================
# Request / Response Models
# ============================================================

class SignupRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="Min 6 characters")
    confirm_password: str = Field(...)
    full_name: str = Field(..., min_length=1)


class LoginRequest(BaseModel):
    email: str = Field(...)
    password: str = Field(...)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    theme_preference: Optional[str] = None


# ============================================================
# Auth Dependency
# ============================================================

async def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract and validate JWT from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid authorization header")

    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)

    if not payload:
        raise HTTPException(401, "Token expired or invalid. Please log in again.")

    if payload.get("type") != "access":
        raise HTTPException(401, "Invalid token type")

    um = get_user_manager()
    user = um.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(401, "User account not found")

    return user


# ============================================================
# Routes
# ============================================================

@router.post("/signup", response_model=TokenResponse)
async def signup(req: SignupRequest):
    """Create a new user account."""
    um = get_user_manager()

    if req.password != req.confirm_password:
        raise HTTPException(400, "Passwords do not match.")

    if len(req.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters.")

    try:
        user = um.create_user(req.email, req.password, req.full_name)
    except ValueError as e:
        raise HTTPException(409, str(e))

    access = create_access_token(user["id"], user["email"], user["full_name"])
    refresh = create_refresh_token(user["id"])

    logger.info(f"New signup: {user['email']}")
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user={
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "onboarding_complete": user["onboarding_complete"],
        },
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Authenticate and return tokens."""
    um = get_user_manager()

    user = um.authenticate(req.email, req.password)
    if not user:
        raise HTTPException(401, "Invalid email or password.")

    access = create_access_token(user["id"], user["email"], user["full_name"])
    refresh = create_refresh_token(user["id"])

    logger.info(f"Login: {user['email']}")
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user={
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "onboarding_complete": bool(user["onboarding_complete"]),
            "theme_preference": user.get("theme_preference", "dark"),
        },
    )


@router.post("/refresh")
async def refresh_token(authorization: Optional[str] = Header(None)):
    """Refresh an expired access token using a valid refresh token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing refresh token")

    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid or expired refresh token. Please log in again.")

    um = get_user_manager()
    user = um.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(401, "User not found")

    access = create_access_token(user["id"], user["email"], user["full_name"])
    return {"access_token": access, "token_type": "bearer"}


@router.get("/me")
async def get_profile(user=Depends(get_current_user)):
    """Get current user's profile."""
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "onboarding_complete": bool(user["onboarding_complete"]),
        "theme_preference": user.get("theme_preference", "dark"),
        "created_at": user["created_at"],
    }


@router.put("/me")
async def update_profile(req: UpdateProfileRequest, user=Depends(get_current_user)):
    """Update user profile."""
    um = get_user_manager()
    updates = {}
    if req.full_name is not None:
        updates["full_name"] = req.full_name
    if req.theme_preference is not None:
        updates["theme_preference"] = req.theme_preference
    if updates:
        um.update_user(user["id"], **updates)
    return {"status": "updated"}


@router.post("/onboarding/complete")
async def complete_onboarding(user=Depends(get_current_user)):
    """Mark onboarding as complete for the current user."""
    um = get_user_manager()
    um.complete_onboarding(user["id"])
    return {"status": "onboarding_complete"}


@router.post("/data/clear")
async def clear_user_data(user=Depends(get_current_user)):
    """Clear all user data (workflows, memory, conversations)."""
    um = get_user_manager()
    um.delete_user_data(user["id"])
    return {"status": "data_cleared"}


@router.get("/data/export")
async def export_user_data(user=Depends(get_current_user)):
    """Export all user data as JSON."""
    um = get_user_manager()
    data = um.export_user_data(user["id"])
    return data
