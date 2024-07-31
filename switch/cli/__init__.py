import click

from switch.cli.ftpserver import ftpserver
from switch.cli.upload import upload


@click.group()
def cli():
    pass


cli.add_command(ftpserver)
cli.add_command(upload)


if __name__ == "__main__":
    cli()
