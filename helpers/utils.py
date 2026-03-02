def get_latest_appimage_data(app_url: str):

    url = f"https://api.github.com/repos/{app_url}/releases/latest"

    return "GET " + url
