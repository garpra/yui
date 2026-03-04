from helpers.utils import read_repository, remove_appimage, remove_repository


def delete_app(args):
    # Ambil data input
    app_url = args.app_url
    # Ambil data repo
    data = read_repository()

    for repo_app_url in data:
        # Cek jika input ada di repo
        if app_url == repo_app_url:
            app_path = data[repo_app_url]["app_path"]

            print(f"Found {app_url}")

            print("\nDeleting app...")
            # Hapus data app dari repo
            remove_repository(app_url)
            # Hapus appimage dari app
            remove_appimage(app_path)
            return

    print("Application is not installed and cannot be removed")
