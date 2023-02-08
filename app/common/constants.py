"""
Store for all public constants.
"""
import os

USERS_COLLECTION = "users"
DIALOGS_COLLECTION = "dialogs"
DIALOG_MESSAGES_COLLECTION = "dialog_messages"

PUBLIC_FOLDER = "public"

FRONTEND_URL = os.getenv("CLIENT_URL", "http://localhost:5173")
SELF_URL = os.getenv("APP_URL", "http://localhost:8000")

cookie_options = {
    "httponly": True,
    "secure": True,
    "max_age": 60 * 60 * 24 * 7 * 4,
}