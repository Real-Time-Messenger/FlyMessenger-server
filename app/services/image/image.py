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
    def _url(url: str, folder: str = "uploads") -> str:
        """
        Build image URL.

        :param url: Image URL.

        :return: Image URL.
        """
        return f"{SELF_URL}/{PUBLIC_FOLDER}/{folder}/{url}"

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

        image_data = base64.b64decode(image["data"])

        image_name = f"{uuid4()}.png"
        with open(f"{PUBLIC_FOLDER}/{folder}/{image_name}", "wb") as f:
            f.write(image_data)

        return ImageService._url(image_name, folder)

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

        await image.seek(0)
        content = await image.read()
        with open(f'{PUBLIC_FOLDER}/{folder}/{image_name}', 'wb') as f:
            f.write(content)

        return ImageService._url(image_name, folder)

    @staticmethod
    async def upload_bytes_image(file: bytes, folder: str = 'uploads') -> str:
        """
        Upload image from bytes.

        :param file: Bytes file.

        :return: Image URL.
        """

        image_name = f'{uuid4()}.png'
        with open(f'{PUBLIC_FOLDER}/{folder}/{image_name}', 'wb', encoding="utf-8") as f:
            f.write(file)

        return ImageService._url(image_name, folder)

    @staticmethod
    async def delete_image(url: str, folder: str = 'uploads') -> None:
        """
        Delete image.

        :param url: Image URL.
        :param folder: Folder name.
        """
        import os

        try:
            os.remove(f'{PUBLIC_FOLDER}/{folder}/{url.split("/")[-1]}')
        except FileNotFoundError:
            pass