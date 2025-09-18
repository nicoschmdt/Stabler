import os

import aiohttp
from aiohttp.client_exceptions import ServerDisconnectedError

URL = os.getenv("BLUEOS_URL") or "http://host.docker.internal"
GITHUB = "https://api.github.com/repos/bluerobotics/BlueOS/releases?per_page=100"


class Requester:
    VERSIONCHOOSER = f"{URL}/version-chooser/v1.0/version"

    CURRENT = f"{VERSIONCHOOSER}/current"
    AVAILABLE_LOCAL = f"{VERSIONCHOOSER}/available/local"
    PULL = f"{VERSIONCHOOSER}/pull/"

    async def post_request(self, endpoint: str, info: dict) -> None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=info) as response:
                    await response.read()
        except ServerDisconnectedError:
            return

    async def get_request(self, endpoint: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint) as response:
                if response.status == 200:
                    return await response.json()
                raise ValueError(
                    f"HTTP {response.status}: Failed to get request from {endpoint}"
                )

    @classmethod
    async def get_versions(cls) -> list[dict]:
        return await cls.get_request(cls, GITHUB)

    @classmethod
    async def local_versions(cls) -> dict:
        response = await cls.get_request(cls, cls.AVAILABLE_LOCAL)
        return response["local"]

    @classmethod
    async def current_version(cls) -> str:
        response = await cls.get_request(cls, cls.CURRENT)
        return response["tag"]

    @classmethod
    async def change_version(cls, info: dict) -> None:
        await cls.post_request(cls, cls.CURRENT, info)

    @classmethod
    async def pull_version(cls, info: dict) -> None:
        await cls.post_request(cls, cls.PULL, info)
