from helpers.utils import get_latest_appimage_data


def install_app(args):
    app_url = args.app_url

    print(f"\nSearch info AppImage for: {app_url}\n")

    result = get_latest_appimage_data(app_url)

    print(result)
