import base64
from uuid import uuid4

from fastapi import UploadFile

from app.common.constants import PUBLIC_FOLDER, SELF_URL


class ImageService:

    @staticmethod
    async def upload_base64_image(
            image: dict,
    ) -> str:
        """ Upload image from base64. """

        image_bytes = base64.b64decode(image['data'].split(',')[1])
        image_name = f'{uuid4()}.png'

        with open(f'{PUBLIC_FOLDER}/{image_name}', 'wb') as f:
            f.write(image_bytes)

        return f'{SELF_URL}/{PUBLIC_FOLDER}/{image_name}'

    @staticmethod
    async def upload_image(
            image: UploadFile,
    ) -> str:
        """ Upload image. """

        image_name = f'{uuid4()}.png'

        with open(f'{PUBLIC_FOLDER}/{image_name}', 'wb') as f:
            f.write(image.file.read())

        return f'{SELF_URL}/{PUBLIC_FOLDER}/{image_name}'