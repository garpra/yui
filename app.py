import argparse


# Temporary func
def install_app(args):
    print("Installing App...")
    print(args.app_url)


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
    install.add_argument("app_url", help="Format: owner/repo")
    install.set_defaults(func=install_app)

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
