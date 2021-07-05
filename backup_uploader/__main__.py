import importlib
import sys

from backup_uploader.chain import BackupChain
from backup_uploader.directories import Counters
from backup_uploader.parser import parse_chain_config_file


def main(argv, argc):
    if argc != 6:
        print(
            "Invalid number of arguments\n"
            f"USAGE: {argv[0]} app_name client credentials_file chain_config upload_file",
            file=sys.stderr,
        )
        sys.exit(1)

    app_name = argv[1]

    counters = Counters(app_name)

    client = argv[2].lower()
    try:
        client_module = importlib.import_module(f"clients.{client}")
    except ImportError:
        print(f"Unknown client clients.{client}", file=sys.stderr)
        sys.exit(2)
    client = getattr(client_module, f"{client.title()}Client")(app_name)

    try:
        with open(argv[3]) as credentials_file:
            client.login(credentials_file)
    except FileNotFoundError:
        print(f'Credentials file "{argv[3]}" not found', file=sys.stderr)
        sys.exit(2)

    chain = BackupChain(client, counters)

    parse_chain_config_file(argv[4], chain)

    with client:
        try:
            chain.store(argv[5])
        except FileNotFoundError:
            print(f'Upload file "{argv[5]}" not found', file=sys.stderr)
            sys.exit(2)

    counters.save()


if __name__ == '__main__':
    main(sys.argv, len(sys.argv))
