"""
Mintuu AI Ecosystem — Authentication System
=============================================
JWT-based authentication with bcrypt password hashing.
Email/Password auth with 7-day token expiry and silent refresh.
"""
import uuid
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
import bcrypt

from mintuu_ai_ecosystem.config.settings import settings

logger = logging.getLogger("mintuu.auth")

# ============================================================
# Password Hashing (direct bcrypt — compatible with bcrypt 5.x)
# ============================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

# ============================================================
# JWT Token Management
# ============================================================

def create_access_token(user_id: str, email: str, name: str) -> str:
    """Create a JWT access token valid for 7 days."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.auth.access_token_expire_days)
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.auth.secret_key, algorithm=settings.auth.algorithm)

def create_refresh_token(user_id: str) -> str:
    """Create a refresh token valid for 30 days."""
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.auth.secret_key, algorithm=settings.auth.algorithm)

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, settings.auth.secret_key, algorithms=[settings.auth.algorithm])
        return payload
    except JWTError as e:
        logger.debug(f"Token decode failed: {e}")
        return None

# ============================================================
# User Database Operations
# ============================================================

class UserManager:
    """Manages user CRUD operations on the SQLite users table."""

    def __init__(self, db):
        self.db = db
        self._ensure_users_table()

    def _ensure_users_table(self):
        """Create users table if not exists."""
        with self.db.get_connection() as conn:
            conn.executescript(USERS_SCHEMA_SQL)
            conn.commit()
        logger.info("Users table ensured.")

    def create_user(self, email: str, password: str, full_name: str) -> Dict[str, Any]:
        """Create a new user. Raises ValueError if email exists."""
        email = email.lower().strip()

        # Check existing
        existing = self.get_user_by_email(email)
        if existing:
            raise ValueError("An account with this email already exists.")

        user_id = str(uuid.uuid4())
        hashed = hash_password(password)
        now = datetime.now(timezone.utc).isoformat()

        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO users (id, email, password_hash, full_name, 
                   is_verified, onboarding_complete, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, email, hashed, full_name, 1, 0, now, now),
            )
            conn.commit()

        logger.info(f"User created: {email} ({user_id})")
        return {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "is_verified": True,
            "onboarding_complete": False,
        }

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        email = email.lower().strip()
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None

    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user. Returns user dict or None."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user["password_hash"]):
            return None
        return user

    def complete_onboarding(self, user_id: str):
        """Mark user's onboarding as complete."""
        now = datetime.now(timezone.utc).isoformat()
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE users SET onboarding_complete = 1, updated_at = ? WHERE id = ?",
                (now, user_id),
            )
            conn.commit()

    def update_user(self, user_id: str, **kwargs):
        """Update user fields."""
        now = datetime.now(timezone.utc).isoformat()
        allowed = {"full_name", "is_verified", "onboarding_complete", "theme_preference"}
        fields = []
        values = []
        for key, val in kwargs.items():
            if key in allowed:
                fields.append(f"{key} = ?")
                values.append(val)
        if not fields:
            return
        fields.append("updated_at = ?")
        values.append(now)
        values.append(user_id)
        with self.db.get_connection() as conn:
            conn.execute(
                f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values
            )
            conn.commit()

    def delete_user_data(self, user_id: str):
        """Clear all user-specific data (memory, workflows, etc)."""
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM memories WHERE agent_id LIKE ?", (f"user-{user_id}%",))
            conn.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
            conn.commit()
        logger.info(f"Cleared data for user {user_id}")

    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data as JSON-serializable dict."""
        with self.db.get_connection() as conn:
            user = dict(conn.execute("SELECT id, email, full_name, created_at FROM users WHERE id = ?", (user_id,)).fetchone() or {})
            conversations = [dict(r) for r in conn.execute("SELECT * FROM conversations WHERE user_id = ?", (user_id,)).fetchall()]
            workflows = [dict(r) for r in conn.execute("SELECT * FROM workflows WHERE initiated_by = ?", (user_id,)).fetchall()]
        return {"user": user, "conversations": conversations, "workflows": workflows}


# ============================================================
# SQL Schema for Users Table
# ============================================================

USERS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    is_verified INTEGER DEFAULT 0,
    onboarding_complete INTEGER DEFAULT 0,
    theme_preference TEXT DEFAULT 'dark',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
"""
