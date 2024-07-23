from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from urllib.parse import urlparse
import click
import os
import subprocess
import shutil
import sys
import tempfile
import uuid
import time


def uuid7():

    # https://antonz.org/uuidv7/#python

    # random bytes
    value = bytearray(os.urandom(16))

    # current timestamp in ms
    timestamp = int(time.time() * 1000)

    # timestamp
    value[0] = (timestamp >> 40) & 0xFF
    value[1] = (timestamp >> 32) & 0xFF
    value[2] = (timestamp >> 24) & 0xFF
    value[3] = (timestamp >> 16) & 0xFF
    value[4] = (timestamp >> 8) & 0xFF
    value[5] = timestamp & 0xFF

    # version and variant
    value[6] = (value[6] & 0x0F) | 0x70
    value[8] = (value[8] & 0x3F) | 0x80

    return uuid.UUID(bytes=bytes(value))


# WORKER LOGIC


def file_to_temp_dir(source, task_name, name=None):

    task_id = uuid7()

    # Create a temporary directory with the UUID name
    temp_dir = os.path.join(tempfile.gettempdir(), task_name, str(task_id))
    os.makedirs(temp_dir)

    # Define the destination file path
    dest = os.path.join(temp_dir, name or os.path.basename(source))

    # Move the file to the new directory

    shutil.move(source, dest)

    return temp_dir, task_id, dest


def filter_files(files):
    for file in map(os.path.realpath, files):
        if not os.path.exists(file):
            click.echo("file {file} does not exists".format(file=file), err=True)
        else:
            yield file


def move_and_run(file):

    temp, task_id, path = file_to_temp_dir(file, "switch_task_run")

    click.echo("Running {path}".format(path=path))

    subprocess.Popen(
        [
            "/opt/homebrew/bin/screen",
            "-L",
            "-Logfile",
            os.path.join(temp, "screen.log"),
            "-S",
            "cmd-{task_id}".format(task_id=task_id),
            "-dm",
            "/bin/sh",
            path,
        ],
        stdin=subprocess.PIPE,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=os.environ,
    )


# FTP SERVER LOGIC


def validate_url(ctx, param, value):
    for v in value:
        try:
            parsed_url = urlparse(v, scheme="file")  # Parse the FTP URL

            if parsed_url.scheme.lower() != "file":
                raise click.BadParameter(
                    "Only File URLs are supported. %s" % (parsed_url,)
                )

            if parsed_url.hostname not in ("localhost", "", None):
                raise click.BadParameter(
                    "Only localhost is supported, hostname is %s"
                    % (parsed_url.hostname,)
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
                action(file)


@click.group()
def cli():
    pass


@cli.command(
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

    for folders, action in ((watch, move_and_run),):

        if folders := tuple(filter_files(folders)):

            for folder in folders:

                for file in os.scandir(folder):
                    action(file.path)

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


if __name__ == "__main__":
    cli()
