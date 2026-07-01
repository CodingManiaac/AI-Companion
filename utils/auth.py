"""
Authentication utilities for AI Study Companion.
Handles password hashing, user registration, login, and session management.
"""

import bcrypt
import streamlit as st
from database.db import create_user, get_user_by_email


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def register_user(name: str, email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success, message) tuple.
    """
    # Validation
    if not name or not email or not password:
        return False, "All fields are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."

    # Check if user already exists
    existing = get_user_by_email(email)
    if existing:
        return False, "An account with this email already exists."

    # Create user
    pw_hash = hash_password(password)
    user_id = create_user(name, email, pw_hash)
    if user_id:
        return True, "Account created successfully! You can now log in."
    return False, "An error occurred. Please try again."


def login_user(email: str, password: str) -> tuple[bool, str | dict]:
    """
    Authenticate a user.
    Returns (success, user_dict | error_message).
    """
    if not email or not password:
        return False, "Please enter both email and password."

    user = get_user_by_email(email)
    if not user:
        return False, "No account found with this email."

    if verify_password(password, user["password_hash"]):
        # Return user info (without the password hash)
        return True, {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "created_at": user["created_at"],
        }
    return False, "Incorrect password."


def logout():
    """Clear the session state to log out the user."""
    keys_to_clear = [
        "authenticated", "user", "current_page",
        "quiz_data", "quiz_submitted", "flashcards",
        "chat_messages", "current_doc_id",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def is_authenticated() -> bool:
    """Check if the current session is authenticated."""
    return st.session_state.get("authenticated", False)


def get_current_user() -> dict | None:
    """Get the currently logged-in user from session state."""
    if is_authenticated():
        return st.session_state.get("user")
    return None


def require_auth():
    """
    Guard that stops page execution if user is not authenticated.
    Call at the top of every protected page.
    """
    if not is_authenticated():
        st.warning("⚠️ Please log in to access this page.")
        st.stop()
