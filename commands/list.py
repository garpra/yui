from helpers.utils import get_list_app


def list_app():
    # Ambil data list app
    app_list = get_list_app()

    # Cek jika app kosong
    if not app_list:
        print("No applications found")
        return

    print("Installed app:")
    for app_url in get_list_app():
        print(app_url)
