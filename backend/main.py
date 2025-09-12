from robyn import Robyn, Request
from version_service import execute_install, get_stable_versions, sync_stables, get_last_updated_timestamp, validate_request
from loguru import logger

SERVICE_NAME = "Stabler"

app = Robyn(__name__)

logger.add(f"Starting {SERVICE_NAME}")

@app.get("/stable-versions")
async def get_versions():
    stable_versions = await get_stable_versions()

    return {"stables": stable_versions}


@app.get("/sync")
async def sync():
    timestamp = await sync_stables()
    return {"timestamp": timestamp}


@app.get("/last-updated")
async def get_last_updated():
    timestamp = await get_last_updated_timestamp()
    return {"timestamp": timestamp}

@app.get("/download")
async def download_stable_version(request: Request):
    try:
        version = request.query_params.get("version", None)
        
        valid, message = validate_request(version)
        if not valid:
            return {"error": message}

        info = {
            "repository": "bluerobotics/blueos-core",
            "tag": version,
        }

        status = await execute_install(info, version)
        if status:
            return {"status": "success", "message": f"Downloaded and applied version {version}"}
        else:
            return {"error": "Failed to download and apply version"}
        
    except Exception as e:
        return {"error": f"Failed to process request: {str(e)}"}


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
