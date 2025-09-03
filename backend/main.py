from robyn import Robyn, Request
from version_service import execute_install, Endpoints, get_request

app = Robyn(__name__)


@app.get("/download")
async def download_stable_version(request: Request):
    try:
        version = request.query_params.get("version", None)
        
        if version not in ["1.3.1", "1.4.2"]:
            return {"error": "Invalid version"}

        current_version_json = await get_request(Endpoints.CURRENT)
        if current_version_json["tag"] == version:
            return {"error": "Version requested is already installed"}

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
        print(f"Error: {e}")
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
