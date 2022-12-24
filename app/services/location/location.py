import httpx

from fastapi import Request

from app.exception.api import APIException


class LocationService:
    """
    Service for location.

    This class is responsible for getting the user's geolocation and getting the user's IP-address.
    """

    @staticmethod
    async def get_ip_address(request: Request) -> str:
        """
        Get user IP-address.

        :param request: Request object.

        :return: User IP-address.
        """

        if not request.headers.get("User-Agent"):
            raise APIException.bad_request("User-Agent header is required.", translation_key="userAgentHeaderIsRequired")

        user_agent = request.headers.get("User-Agent")
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api64.ipify.org?format=json', headers={"User-Agent": user_agent})
            response = response.json()

        return response.get("ip")

    @staticmethod
    async def get_location(ip_address: str) -> dict:
        """
        Get user location.

        :param ip_address: User IP-address.

        :return: User location (in "city, region, country" format).
        """

        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://ipinfo.io/{ip_address}/json")
            response = response.json()

        return {
            "city": response.get("city"),
            "region": response.get("region"),
            "country": response.get("country"),
        }
