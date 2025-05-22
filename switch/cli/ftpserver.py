import os
import pathlib
import sys
from urllib.parse import urlparse

import click
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from switch.utils.files import filter_files
from switch.utils.run import grab_and_run

# FTP SERVER LOGIC


def validate_url(ctx, param, value):
    for v in value:
        try:
            parsed_url = urlparse(v, scheme="file")  # Parse the FTP URL

            if parsed_url.scheme.lower() != "file":
                raise click.BadParameter(
                    "Only File URLs are supported. {}".format(parsed_url)
                )

            if parsed_url.hostname not in ("localhost", "", None):
                raise click.BadParameter(
                    "Only localhost is supported, hostname is {}".format(
                        parsed_url.hostname
                    )
                )

        except ValueError:
            raise click.BadParameter(
                'Invalid FILE URL format. It should be in the form "file://user:admin@localhost/path/to/folder"'
            )

        yield parsed_url


class ActionFTPHandler(FTPHandler):
    folder_actions = {}

    def on_file_received(self, file):
        for path, action in self.folder_actions.items():
            if file.startswith(path):
                action(pathlib.Path(file))


@click.command(
    help="Start an ftp server. Use a list of urls such as file://user:admin@localhost/path/to/folder to define folders"
)
@click.option("--host", default="0.0.0.0", help="Host IP address to bind to")
@click.option("--port", default=7500, help="Port number to bind to")
@click.option("--perm", default=None, help="Permission string")
@click.option(
    "--watch", multiple=True, type=click.Path(), help="Folders to watch for changes"
)
@click.argument("urls", nargs=-1, callback=validate_url)
def ftpserver(host, port, perm, urls, watch):
    authorizer = DummyAuthorizer()

    for url in urls:
        click.echo(str(url))

        authorizer.add_user(
            url.username or "admin",
            url.password or "admin",
            url.path or ".",
            perm=perm or "elradfmwMT",
        )

    handler = ActionFTPHandler
    handler.authorizer = authorizer
    handler.permit_foreign_addresses = True
    handler.passive_ports = range(port, port + 1)

    for folders, action in ((watch, grab_and_run),):
        if folders := tuple(filter_files(folders)):
            for folder in folders:
                for file in os.scandir(folder):
                    action(file)

                click.echo("Watching folder {folder} for changes".format(folder=folder))

                handler.folder_actions[folder] = action

    click.echo(
        (
            "Starting ftp server at {protocol}://{addr}:{port}/\n"
            "Quit the process with {quit_command}.\n"
        ).format(
            protocol="ftp",
            addr=host,
            port=port,
            quit_command="CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C",
        )
    )

    server = FTPServer((host, port), handler)
    server.serve_forever()
