from helpers.utils import (
    appimage_exists,
    download,
    get_latest_appimage_data,
    update_repository,
)


def install_app(args):
    app_url = args.app_url

    print(f"Search info AppImage for: {app_url}\n")

    # Ambil data versi terbaru dari repo
    results = get_latest_appimage_data(app_url)

    # Cek jika ambil data success
    if not results["success"]:
        print(f"Failed to get data: {results["status"]}\n")
        return

    app_name = results["app_name"]
    app_path = results["app_path"]
    version = results["version"]
    download_url = results["download_url"]

    print(f"Found: {app_name} {version}\n")

    # Cek jika appimage sudah ada dan versi terbaru
    if appimage_exists(app_name):
        print(f"{app_url} has been downloaded and is the latest version")
        return

    # Download AppImage sesuai dengan url dan path
    download(download_url, app_path)

    # Update repository data
    update_repository(app_url, app_name, app_path, version, download_url)

    print(f"\nDownload {app_name} successfully")
