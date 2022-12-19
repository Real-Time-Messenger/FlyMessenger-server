import httpx

from fastapi import Request


class LocationService:

    @staticmethod
    async def get_ip_address(request: Request) -> str:
        user_agent = request.headers.get("User-Agent")
        async with httpx.AsyncClient() as client:
            response = await client.get('https://api64.ipify.org?format=json', headers={"User-Agent": user_agent})
            response = response.json()

        return response.get("ip")

    @staticmethod
    async def get_location(ip_address: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://ipinfo.io/{ip_address}/json")
            response = response.json()

        return {
            "city": response.get("city"),
            "region": response.get("region"),
            "country": response.get("country"),
        }
