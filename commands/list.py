from helpers.repository import get_list_app


def list_app(args):
    """
    Tampilkan semua aplikasi AppImage yang terinstal.

    Mengambil dan menampilkan semua aplikasi yang telah diinstal melalui Yui
    dari repositori lokal. Setiap entri ditampilkan dalam format 'owner/repo'.
    """
    # Ambil data list app
    app_list = get_list_app()

    # Cek jika app kosong
    if not app_list["github_app"] and not app_list["local_app"]:
        print("No applications found")
        return

    print("Installed app:")

    # Print github app
    if app_list["github_app"]:
        print(">> Github App:")
        for app_url in app_list["github_app"]:
            print(f"- {app_url}")

    if app_list["github_app"] and app_list["local_app"]:
        print()

    # Print local app
    if app_list["local_app"]:
        print(">> Local App:")
        for app_url in app_list["local_app"]:
            print(f"- {app_url}")
