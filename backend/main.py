"""
Stabler is a service that allows you to download and apply stable versions of BlueOS.
"""

from loguru import logger
from robyn import Request, Robyn

from stabler import Stabler

SERVICE_NAME = "Stabler"

app = Robyn(__name__)
stabler = Stabler()

logger.add(f"Starting {SERVICE_NAME}")


@app.get("/stable-versions")
async def get_versions():
    stable_versions = await stabler.get_stable_versions()

    return {"stables": stable_versions}


@app.get("/sync")
async def sync():
    timestamp = await stabler.update_stables()
    return {"timestamp": timestamp}


@app.get("/last-updated")
async def get_last_updated():
    timestamp = await stabler.get_timestamp()
    return {"timestamp": timestamp}


@app.get("/download")
async def download_stable_version(request: Request):
    version = request.query_params.get("version", None)

    valid, message = await stabler.pull_and_apply(version)
    if not valid:
        return {"status": 400, "message": message}
    return {"status": 200, "message": f"Downloaded and applied version {version}"}


def main():
    app.serve_directory(
        route="/",
        directory_path="/frontend",
        index_file="index.html",
        show_files_listing=False,
    )
    app.start(host="0.0.0.0", port=8123, _check_port=False)


if __name__ == "__main__":
    main()
