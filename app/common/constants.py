"""
Store for all public constants.
"""

USERS_COLLECTION = "users"
DIALOGS_COLLECTION = "dialogs"
DIALOG_MESSAGES_COLLECTION = "dialog_messages"

PUBLIC_FOLDER = "public"

FRONTEND_URL = "http://localhost:3000/m"
SELF_URL = "http://localhost:8000"

cookie_options = {
    "max_age": 60 * 60 * 24 * 7 * 4,
}