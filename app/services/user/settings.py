from app.models.user.user import UserModel, UserInResponseModel


class SettingsService:
    """
    Service for settings.

    This class is responsible for performing tasks when a user changes their settings.
    """

    @staticmethod
    async def validate_user_settings(user: UserModel) -> UserInResponseModel:
        """
        Validate user settings.

        :param user: User object.

        :return: User object.
        """
        if not user.settings.last_activity_mode:
            user.last_activity = None
            user.is_online = None

        return UserInResponseModel(**user.dict())