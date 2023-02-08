import bcrypt

class HashService:
    """
    Hash service.

    This service is used to hash and compare passwords.
    """

    @staticmethod
    def get_hash(password: str) -> str:
        """
        Hash a password for storing.

        :param password: Password to hash.

        :return: Hashed password.
        """

        return bcrypt.hashpw(password=password.encode("utf-8"), salt=bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def is_hashed(password: str) -> bool:
        """
        Check if a password is hashed.

        :param password: Password to check.

        :return: True if password is hashed, False otherwise.
        """

        return password.startswith("$2b$") and len(password) == 60

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a stored password against one provided by user.

        :param plain_password: Password to check.
        :param hashed_password: Hashed password.

        :return: True if password is correct, False otherwise.
        """

        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
