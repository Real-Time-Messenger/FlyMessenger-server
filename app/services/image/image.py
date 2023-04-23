import base64
import colorsys
import random
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from fastapi import UploadFile

from app.common.constants import PUBLIC_FOLDER, SELF_URL
from app.models.user.user import UserModel


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

    @staticmethod
    async def generate_mock_image(username: str) -> str:
        """
        Generate mock image.

        :param username: Username.

        :return: Image URL, which is generated from the initials of the username or firstname.
        """

        initials = username[:2].upper()

        background_colors, text_colors = ImageService.generate_color_palette()

        size = 200

        image = Image.new('RGB', (size, size), color=random.choice(background_colors))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('arial.ttf', 80)
        text_size = draw.textsize(initials, font=font)
        text_position = ((size - text_size[0]) / 2, (size - text_size[1]) / 2)
        draw.text(text_position, initials, fill=random.choice(text_colors), font=font)

        image_name = f'{uuid4()}.png'
        image.save(f'{PUBLIC_FOLDER}/avatars/{image_name}')

        return ImageService._url(image_name, "avatars")

    @staticmethod
    def generate_color_palette() -> list:
        """
        Generate color palette.

        :return: Color palette with background and text colors.
        """

        NUM_COLORS = 5

        hue = random.random()
        saturation = 0.5
        value = 0.5
        start_color = colorsys.hsv_to_rgb(hue, saturation, value)

        background_colors = []
        text_colors = []
        for i in range(NUM_COLORS):
            hue += 0.1
            hue %= 1
            next_color = colorsys.hsv_to_rgb(hue, saturation, value)

            if (0.2126 * next_color[0] + 0.7152 * next_color[1] + 0.0722 * next_color[2]) > 0.5:
                background_colors.append(tuple(int(c * 255) for c in start_color))
                text_colors.append(tuple(int(c * 255) for c in next_color))
            else:
                background_colors.append(tuple(int(c * 255) for c in next_color))
                text_colors.append(tuple(int(c * 255) for c in start_color))

            start_color = next_color

        return background_colors, text_colors
