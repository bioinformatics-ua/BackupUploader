import importlib
import sys

import click

from backup_uploader.chain import BackupChain
from backup_uploader.clients.exceptions import BaseClientException
from backup_uploader.directories import Counters
from backup_uploader.parser import InvalidChainConfig, parse_chain_config_file


@click.command()
@click.argument(
    "app_name",
    type=click.STRING,
    required=True,
)
@click.argument(
    "client",
    type=click.STRING,
    required=True,
)
@click.argument(
    "credentials_file",
    type=click.File("r"),
    required=True,
)
@click.argument(
    "chain_config",
    type=click.STRING,
    required=True,
)
@click.argument(
    "upload_file",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=False,
    ),
    required=True,
)
def main(
    app_name,
    client,
    credentials_file,
    chain_config,
    upload_file,
):
    counters = Counters(app_name)

    client = client.lower()
    try:
        client_module = importlib.import_module(f"backup_uploader.clients.{client}")
    except ImportError:
        click.echo(f"Unknown client clients.{client}", err=True)
        return 1
    client = getattr(client_module, f"{client.title()}Client")(app_name)

    try:
        client.login(credentials_file)
    except BaseClientException as ex:
        click.echo(ex.message, err=True)
        return 1

    chain = BackupChain(client, counters)

    try:
        parse_chain_config_file(chain_config, chain)
    except InvalidChainConfig as ex:
        click.echo(ex.message, err=True)
        return 1

    with client:
        chain.store(upload_file)

    counters.save()


if __name__ == '__main__':
    main(sys.argv[1:])
