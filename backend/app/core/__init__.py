"""
Core package containing configuration and authentication.
"""
from .config import settings
from .database import get_db, init_db, Base
from .firebase_auth import get_current_user, verify_firebase_token

__all__ = ["settings", "get_db", "init_db", "Base", "get_current_user", "verify_firebase_token"]
