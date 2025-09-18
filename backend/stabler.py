import asyncio
import re
from datetime import datetime

from aiohttp.client_exceptions import ClientConnectorError
from loguru import logger
from semver import Version

from storage import Storage
from requester import Requester

STABLE_PATTERN = re.compile(r"\d\.\d\.\d$")


class Stabler:
    def __init__(self):
        self.storage = Storage()

    async def get_stables(self) -> list[str]:
        content = self.storage.read_stables()
        if content:
            return content

        await self.update_stables()
        return self.storage.read_stables()

    async def get_timestamp(self) -> str:
        content = self.storage.read_last_updated()
        if content:
            return content

        return await self.update_stables()

    async def update_stables(self) -> str:
        stables = await self.get_latest_stables()
        self.storage.write_stables(stables)

        updated_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.storage.write_last_updated(updated_timestamp)

        return updated_timestamp

    async def get_latest_stables(self) -> list[str]:
        versions = await Requester.get_versions()
        return sorted(filter_stables(versions, "tag_name"), reverse=True)

    async def requires_download(self, version: str) -> bool:
        local_images = await Requester.local_versions()
        return version not in filter_stables(local_images, "tag")

    async def install(self, info: dict, version: str) -> bool:
        if await self.requires_download(version):
            logger.info(f"Version {version} is not in the local images, pulling it...")
            await Requester.pull_version(info)
            await asyncio.sleep(10)

            if await self.requires_download(version):
                return False

        logger.info(f"Changing version to {version}")
        await Requester.change_version(info)
        await asyncio.sleep(10)
        logger.info(f"Checking if version is expected: {version}")
        return await self.validate(version)

    async def validate(self, version: str, delay: int = 20) -> bool:
        while True:
            try:
                current_version = await Requester.current_version()
                return current_version == version
            except (ClientConnectorError, ValueError):
                await asyncio.sleep(delay)
            except Exception:
                return False

    async def pull_and_apply(self, version: str) -> [bool, str]:
        try:
            if version not in await self.get_stables():
                return False, "Invalid version"

            current_version = await Requester.current_version()
            if current_version == version:
                return False, "Version requested is already installed"

            info = {
                "repository": "bluerobotics/blueos-core",
                "tag": version,
            }

            status = await self.install(info, version)
            if status:
                return True, f"Downloaded and applied version {version}"
            return False, "Failed to download and apply version"

        except Exception as e:
            return False, f"Failed to download and apply version: {str(e)}"

    async def get_stable_versions(self) -> list[str]:
        stables = await self.get_stables()
        current_str = await Requester.current_version()

        try:
            current = Version.parse(current_str)

            enabled_versions = []
            for stable_str in stables:
                stable = Version.parse(stable_str)
                if current.is_compatible(stable) and (
                    current.prerelease is not None or stable >= current
                ):
                    enabled_versions.append(stable_str)

            return enabled_versions
        except ValueError:
            return stables[:4]


def filter_stables(stables: list[str], filter: str) -> list[str]:
    return list(
        {
            version[filter]
            for version in stables
            if STABLE_PATTERN.match(version[filter])
            and (
                filter == "tag_name"
                or version.get("repository", "") == "bluerobotics/blueos-core"
            )
        }
    )
