import argparse
import re
from commands.install import install_app
from commands.list import list_app
from commands.update import update_app


# Repo cek format repo app
def repo_type(text):
    # Regex format owner/repo
    pattern = r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$"

    # Cek jika input tidak sesuai format
    if not re.match(pattern, text):
        raise argparse.ArgumentTypeError(
            "Invalid format {text}, format is 'owner/repo'"
        )

    return text


def main():
    # Buat parser
    parser = argparse.ArgumentParser(
        prog="yui", description="Yui - AppImage manager for Linux"
    )
    # Buat subparser
    subparser = parser.add_subparsers(dest="command")

    # Subcommand Install
    install = subparser.add_parser(
        "install", help="Download and install AppImage from Github"
    )
    install.add_argument("app_url", help="Format: owner/repo", type=repo_type)
    install.set_defaults(func=install_app)

    # Subcommand list
    list = subparser.add_parser("list", help="Get all list of app")
    list.set_defaults(func=list_app)

    # Subcommand update
    update = subparser.add_parser("update", help="Update all app from repository")
    update.set_defaults(func=update_app)

    # Mengambil seluruh parser dari input
    args = parser.parse_args()

    # Tampilkan bantuan jika user tidak mengetik Subcommand
    # dengan mengecek jika args ada attribute 'func'
    if args.command == "list":
        args.func()
    elif args.command == "update":
        args.func()
    elif hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
