import base64
import random
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from fastapi import UploadFile

from app.common.constants import PUBLIC_FOLDER, SELF_URL


class ImageService:
    """
    Service for image.

    This class is responsible for performing tasks when image is created, updated, deleted, etc.
    """

    @staticmethod
    def _url(
            filename: str,
            folder: str = "uploads"
    ) -> str:
        """
        Generate image URL.

        :param filename: Image filename.
        :param folder: Folder name.

        :return: Image URL.
        """

        return f"{SELF_URL}/{PUBLIC_FOLDER}/{folder}/{filename}"

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

        while True:
            # Generate random background color
            background_color = ImageService.generate_random_color()
            background_color_brightness = ImageService.calculate_color_brightness(background_color)

            # Check if background color brightness is high enough
            if background_color_brightness >= 125:
                break

        while True:
            # Generate random text color
            text_color = ImageService.generate_random_color()
            text_color_brightness = ImageService.calculate_color_brightness(text_color)

            # Check if text color contrast with background is high enough
            contrast_ratio = ImageService.get_contrast_ratio(background_color, text_color)
            if contrast_ratio >= 4.5:
                break

        size = 200

        image = Image.new('RGB', (size, size), color=background_color)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('public/fonts/regular.ttf', size=100)
        text_size = draw.textsize(initials, font=font)
        text_position = ((size - text_size[0]) / 2, (size - text_size[1]) / 2)
        draw.text(text_position, initials, fill=text_color, font=font)

        image_name = f'{uuid4()}.png'
        image.save(f'{PUBLIC_FOLDER}/avatars/{image_name}')

        return ImageService._url(image_name, 'avatars')

    @staticmethod
    def generate_random_color() -> tuple:
        """
        Generate random color.

        :return: Random RGB color.
        """

        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        return (r, g, b)

    @staticmethod
    def calculate_color_brightness(color: tuple) -> float:
        """
        Calculate color brightness.

        :param color: RGB color.

        :return: Color brightness.
        """

        r, g, b = color
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness

    @staticmethod
    def get_contrast_ratio(color1: tuple, color2: tuple) -> float:
        """
        Get contrast ratio between two colors.

        :param color1: RGB color.
        :param color2: RGB color.

        :return: Contrast ratio.
        """

        brightness1 = ImageService.calculate_color_brightness(color1)
        brightness2 = ImageService.calculate_color_brightness(color2)

        if brightness1 > brightness2:
            return (brightness1 + 0.05) / (brightness2 + 0.05)

        return (brightness2 + 0.05) / (brightness1 + 0.05)


