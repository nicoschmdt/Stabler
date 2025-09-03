import asyncio
import aiohttp
import os

url = os.getenv("BLUEOS_URL") or "http://host.docker.internal"
base_endpoint = f"{url}/version-chooser/v1.0"

class Endpoints:
    CURRENT = f"{base_endpoint}/version/current"
    AVAILABLE_LOCAL = f"{base_endpoint}/version/available/local"
    PULL = f"{base_endpoint}/version/pull/"


async def post_request(endpoint: str, info: dict) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=info) as response:
            await response.read()


async def post_request_no_wait(endpoint: str, info: dict) -> None:
    async with aiohttp.ClientSession() as session:
        await session.post(endpoint, json=info)


async def get_request(endpoint: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint) as response:
            return await response.json()


async def is_expected_version(version: str, max_attempts: int = 5, delay: int = 20) -> bool:
    for _ in range(max_attempts):
        try:
            response_json = await get_request(Endpoints.CURRENT)
            current_version = response_json.get("tag")
            if current_version == version:
                return True
        except Exception as e:
            await asyncio.sleep(delay)
            # Cannot connect to host blueos-avahi.local:80 ssl:default [Connect call failed ('192.168.100.37', 80)]
            # <class 'aiohttp.client_exceptions.ClientConnectorError'>
    return False


async def blueos_stable_version_available(version: str) -> bool:
    local_images = await get_request(Endpoints.AVAILABLE_LOCAL)
    blueos_images = [image["tag"] for image in local_images["local"] if image["repository"] == "bluerobotics/blueos-core"]
    return version in blueos_images


async def install_version(info: dict) -> None:
    try:
        print("Applying version...")
        async with aiohttp.ClientSession() as session:
            await session.post(f"{base_endpoint}/version/current", json=info)
    except Exception:
        pass


async def execute_install(info: dict, version: str) -> bool:
    print(f"Executing install for version: {version}")
    if not await blueos_stable_version_available(version):
        print(f"Pulling version: {version}")
        await post_request(Endpoints.PULL, info)
    print(f"Installing version: {version}")
    await install_version(info)
    await asyncio.sleep(10) # esperar 10 segundos para o blueos instalar a versão
    print(f"Checking if version is expected: {version}")
    return await is_expected_version(version)