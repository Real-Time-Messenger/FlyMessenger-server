from app.models.user.user import UserModel, UserInResponseModel


class SettingsService:

    @staticmethod
    async def validate_user_settings(user: UserModel) -> UserInResponseModel:
        if not user.settings.is_display_name_visible:
            user.first_name = None
            user.last_name = None

        if not user.settings.is_email_visible:
            user.email = None

        if not user.settings.last_activity_mode:
            user.last_activity = None
            user.is_online = None

        return UserInResponseModel(**user.dict())