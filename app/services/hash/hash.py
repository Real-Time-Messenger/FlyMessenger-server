import bcrypt

class HashService:

    @staticmethod
    def get_hash(password: str) -> str:
        """ Hash a password for storing. """

        return bcrypt.hashpw(password=password.encode("utf-8"), salt=bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def is_hashed(password: str) -> bool:
        """ Check if a password is hashed. """

        return password.startswith("$2b$") and len(password) == 60

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """ Verify a stored password against one provided by user. """

        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))