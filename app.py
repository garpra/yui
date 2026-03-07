import argparse
import re
from commands.install import install_app
from commands.list import list_app
from commands.update import update_app
from commands.delete import delete_app


# Repo cek format repo app
def repo_type(text):
    """
    Validasi jika string input sesuai dengan format 'owner/repo'.

    Fungsi ini digunakan untuk validator tipe custom untuk argumen argparse agar memastikan
    bahwa URL dari repositori sesuai dengan sistem yang dibuat.
    """
    # Regex format owner/repo
    pattern = r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$"

    # Cek jika input tidak sesuai format
    if not re.match(pattern, text):
        raise argparse.ArgumentTypeError(
            f"Invalid format '{text}', format is 'owner/repo'"
        )

    return text


def main():
    """
    Fungsi utama untuk aplikasi CLI Yui.

    Membuat parser argumen dengan subcommand untuk mengelola aplikasi AppImage:
    - install: Download dan instal AppImage dari GitHub
    - list: Tampilkan semua aplikasi AppImage yang terinstal
    - update: Perbarui semua aplikasi yang terinstal ke versi terbaru
    - delete: Hapus aplikasi yang terinstal dari sistem
    """
    # Buat parser
    parser = argparse.ArgumentParser(
        prog="yui", description="Yui - AppImage manager for Linux"
    )
    # Buat subparser
    subparser = parser.add_subparsers(dest="command")

    # Subcommand Install
    install_cmd = subparser.add_parser(
        "install", help="Download and install AppImage from Github"
    )
    install_cmd.add_argument("app_url", help="Format: owner/repo", type=repo_type)
    install_cmd.set_defaults(func=install_app)

    # Subcommand list
    list_cmd = subparser.add_parser("list", help="Get all list of app")
    list_cmd.set_defaults(func=list_app)

    # Subcommand update
    update_cmd = subparser.add_parser("update", help="Update all app from repository")
    update_cmd.set_defaults(func=update_app)

    # Subcommand delete
    delete_cmd = subparser.add_parser("delete", help="Delete app from system")
    delete_cmd.add_argument("app_url", help="Format: owner/repo", type=repo_type)
    delete_cmd.set_defaults(func=delete_app)

    # Mengambil seluruh parser dari input
    args = parser.parse_args()

    # Tampilkan bantuan jika user tidak mengetik Subcommand
    # dengan mengecek jika args ada attribute 'func'
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
