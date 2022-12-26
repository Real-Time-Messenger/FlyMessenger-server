import random
import string

from pydantic import EmailStr


def random_lower_string() -> str:
    """
    Generate a random lower string.

    :return: Random lower string.
    """

    return "".join(random.choices(string.ascii_lowercase, k=20))


def random_email() -> EmailStr:
    """
    Generate a random email.

    :return: Random email.
    """
    available_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]

    return EmailStr(f"{random_lower_string()}@{random.choice(available_domains)}")