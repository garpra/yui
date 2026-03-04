from helpers.utils import download, get_latest_appimage_data, update_repository


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
    version = results["version"]
    download_url = results["download_url"]

    print(f"Found: {app_name} {version}\n")

    # Download AppImage sesuai dengan url dan path
    download(download_url, app_name)

    # Update repository data
    update_repository(app_url, app_name, version, download_url)

    print(f"\nDownload {app_name} successfully")
