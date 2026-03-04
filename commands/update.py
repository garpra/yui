from helpers.utils import (
    download,
    get_latest_appimage_data,
    get_list_app,
    read_repository,
    remove_appimage,
    update_repository,
)


def update_app():
    # Ambil list data dari repo
    list_app = get_list_app()
    # Cek jika list data kosong
    if not list_app:
        print("No application is installed")
        return

    # Ambil semua data dari repo
    data_repo = read_repository()

    for app_url in list_app:
        # Ambil versi app dari repo
        repo_version = data_repo[app_url]["version"]

        # Ambil metadata app terbaru
        new_data = get_latest_appimage_data(app_url)
        new_version = new_data["version"]
        new_download_url = new_data["download_url"]
        new_app_name = new_data["app_name"]
        new_app_path = new_data["app_path"]

        # Cek jika versi app sudah terbaru
        if repo_version == new_version:
            print(f"{app_url} is latest version")
        else:
            # Hapus appimage lama
            remove_appimage(data_repo[app_url]["app_path"])

            # Update app ke versi terbaru
            print(f"Updating {app_url} {new_version}:")
            download(new_download_url, new_app_path)

            # Update repository data
            update_repository(
                app_url, new_app_name, new_app_path, new_version, new_download_url
            )

    print("\nUpdate all application finished")
