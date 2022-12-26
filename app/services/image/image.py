import base64
from uuid import uuid4

from fastapi import UploadFile

from app.common.constants import PUBLIC_FOLDER, SELF_URL


class ImageService:
    """
    Service for image.

    This class is responsible for performing tasks when image is created, updated, deleted, etc.
    """

    @staticmethod
    def _url(url: str) -> str:
        """
        Build image URL.

        :param url: Image URL.

        :return: Image URL.
        """
        return f"{SELF_URL}/{PUBLIC_FOLDER}/{url}"

    @staticmethod
    async def upload_base64_image(
            image: dict,
            folder: str = "uploads"
    ) -> str:
        """
        Upload image from base64.

        :param image: Image object.

        :return: Image URL.
        """

        image_bytes = base64.b64decode(image['data'])
        image_name = f'{uuid4()}.png'

        with open(f'{PUBLIC_FOLDER}/{folder}/{image_name}', 'wb') as f:
            f.write(image_bytes)

        return ImageService._url(image_name)

    @staticmethod
    async def upload_image(
            image: UploadFile,
            folder: str = 'uploads'
    ) -> str:
        """
        Upload image.

        :param image: Image object.

        :return: Image URL.
        """

        image_name = f'{uuid4()}.png'

        with open(f'{PUBLIC_FOLDER}/{folder}/{image_name}', 'wb') as f:
            f.write(await image.read())

        return ImageService._url(image_name)