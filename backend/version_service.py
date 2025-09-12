import asyncio
import aiohttp
import os
import re

from datetime import datetime
from aiohttp.client_exceptions import ClientConnectorError
from loguru import logger
from pathlib import Path

url = os.getenv("BLUEOS_URL") or "http://host.docker.internal"
base_endpoint = f"{url}/version-chooser/v1.0/version"

VERSION_PATTERN = re.compile(r'\d\.\d+')
STABLE_PATTERN = re.compile(r'\d\.\d\.\d$')

class Endpoints:
    CURRENT = f"{base_endpoint}/current"
    AVAILABLE_LOCAL = f"{base_endpoint}/available/local"
    AVAILABLE_REMOTE = f"{base_endpoint}/available/bluerobotics/blueos-core"
    PULL = f"{base_endpoint}/pull/"


text_file = Path("/var/lib/stabler/stables.txt")
last_updated = Path("/var/lib/stabler/last_updated.txt")

# I am still not considering the hash of the stables versions so it is incomplete
async def get_stables() -> list[str]:
    if not text_file.exists():
        await sync_stables()

    with open(text_file, "r") as file:
        return file.read().splitlines()


async def sync_stables() -> str:
    stables = await get_latest_stables()
    last_updated_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(text_file, "w") as file:
        for stable in stables:
            file.write(stable + "\n")

    with open(last_updated, "w") as file:
        file.write(last_updated_timestamp)
    return last_updated_timestamp


async def get_last_updated_timestamp() -> str:
    if not last_updated.exists():
        return await sync_stables()
    with open(last_updated, "r") as file:
        return file.read()


async def validate_request(version: str) -> [bool, str]:
    if version not in get_stables():
        return False, "Invalid version"

    current_version_json = await get_request(Endpoints.CURRENT)
    if current_version_json["tag"] == version:
        return False, "Version requested is already installed"
        
    return True, None


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


async def get_latest_stables() -> list[str]:
    available_versions = await get_request(Endpoints.AVAILABLE_REMOTE)
    available_remote = available_versions["remote"] + available_versions["local"]
    return sorted(list(set([
        version["tag"] for version in available_remote if 
        STABLE_PATTERN.match(version["tag"]) and 
        version["repository"] == "bluerobotics/blueos-core"
    ])), reverse=True)


async def get_stable_versions() -> list[str]:
    stables = await get_stables()
    current_version = await get_request(Endpoints.CURRENT)

    if VERSION_PATTERN.match(current_version["tag"]):
        if STABLE_PATTERN.match(current_version["tag"]):
            enabled_versions = [version for version in stables if version >= current_version["tag"]]
            return enabled_versions
        enabled_versions = []
        for stable in stables:
            if stable[:3] >= current_version["tag"][:3]:
                enabled_versions.append(stable)
        if enabled_versions:
            return enabled_versions
    return stables[:4]


async def validate(version: str, delay: int = 20) -> bool:
    while True:
        try:
            response_json = await get_request(Endpoints.CURRENT)
            current_version = response_json.get("tag")
            if current_version == version:
                return True
            else:
                return False
        except ClientConnectorError:
            await asyncio.sleep(delay)
        except Exception:
            return False


async def blueos_stable_version_available(version: str) -> bool:
    local_images = await get_request(Endpoints.AVAILABLE_LOCAL)
    blueos_images = [image["tag"] for image in local_images["local"] if image["repository"] == "bluerobotics/blueos-core" if STABLE_PATTERN.match(image["tag"])]
    return version in blueos_images


async def execute_install(info: dict, version: str) -> bool:
    logger.info(f"Executing install for version: {version}")
    if not await blueos_stable_version_available(version):
        logger.info(f"Pulling version: {version}")
        await post_request(Endpoints.PULL, info)

    logger.info("Applying version...")
    await post_request(Endpoints.CURRENT, info)
    await asyncio.sleep(10) # esperar 10 segundos para o blueos instalar a versão
    logger.info(f"Checking if version is expected: {version}")
    return await validate(version)