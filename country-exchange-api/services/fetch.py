import httpx
import os

COUNTRIES_URL = os.getenv("COUNTRIES_API")
EXCHANGE_URL = os.getenv("EXCHANGE_API")

async def fetch_countries():
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(COUNTRIES_URL)
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as e:
            raise ExternalAPIError("REST Countries", str(e))

async def fetch_exchange_rates():
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(EXCHANGE_URL)
            resp.raise_for_status()
            data = resp.json()
            if data.get("result") != "success":
                raise ValueError("Invalid response")
            return data["rates"]
        except httpx.RequestError as e:
            raise ExternalAPIError("Exchange Rate API", str(e))

class ExternalAPIError(Exception):
    def __init__(self, api_name: str, detail: str):
        self.api_name = api_name
        self.detail = detail