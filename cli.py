import click
import os
import sys
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from urllib.parse import urlparse
from huey import SqliteHuey
import uuid
import shutil
import tempfile
import subprocess


@click.group()
def cli():
    pass


# WORKER LOGIC


huey = SqliteHuey(filename=os.path.join(os.path.dirname(__file__), "huey.db"))


@huey.task()
def run_script_file(temp, path):
    # Open the log file in write mode

    stderr = os.path.join(temp, "stderr.txt")
    stdout = os.path.join(temp, "stdout.txt")

    with open(stderr, "w") as stdout_file:
        with open(stdout, "w") as stdout_file:
            # Run the script using /bin/sh

            click.echo(
                "{temp} started {name}".format(name=os.path.basename(path), temp=temp),
                err=True,
            )
            result = subprocess.run(
                ("/bin/sh", path), stdout=stdout_file, stderr=stdout_file
            )
            click.echo(
                "{temp} finished with returncode {returncode}".format(
                    temp=temp, returncode=result.returncode
                ),
                err=True,
            )

    for path, err in (
        (stderr, True),
        (stdout, False),
    ):

        if os.path.exists(path):
            with open(path, "r") as log:
                if text := log.read().strip():
                    click.echo(text, err=err)
                else:
                    os.remove(path)


def copy_file_to_temp_dir(source_file):
    # Generate a UUID for the directory name
    dir_uuid = str(uuid.uuid4())

    # Create a temporary directory with the UUID name
    temp_dir = os.path.join(tempfile.gettempdir(), "switch_task_runner", dir_uuid)
    os.makedirs(temp_dir)

    # Define the destination file path
    destination_file = os.path.join(temp_dir, os.path.basename(source_file))

    # Copy the file to the new directory
    shutil.copy(source_file, destination_file)

    return temp_dir, destination_file


@cli.command(help="Starts the task worker")
@click.option("--workers", default=4, help="Number of worker to spawn")
def worker(workers):
    click.echo(
        (
            "Starting {workers} workers\n"
            "Quit the process with {quit_command}.\n"
        ).format(
            workers=workers,
            quit_command="CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C",
        )
    )
    huey.create_consumer(workers=workers).run()


@cli.command(help="Schedule a list of script files for execution")
@click.argument("files", nargs=-1)
def runscript(files):

    for file in map(os.path.realpath, files):
        if not os.path.exists(file):
            click.echo("file {file} does not exists".format(file=file), err=True)
        else:
            click.echo("file exists scheduling")

            run_script_file.schedule(copy_file_to_temp_dir(file), delay=0)


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


@cli.command(
    help="Start an ftp server. Use a list of urls such as file://user:admin@localhost/path/to/folder to define folders"
)
@click.option("--host", default="0.0.0.0", help="Host IP address to bind to")
@click.option("--port", default=7500, help="Port number to bind to")
@click.option("--perm", default=None, help="Permission string")
@click.argument("urls", nargs=-1, callback=validate_url)
def ftpserver(host, port, perm, urls):

    authorizer = DummyAuthorizer()

    for url in urls:

        click.echo(str(url))

        authorizer.add_user(
            url.username or "admin",
            url.password or "admin",
            url.path or ".",
            perm=perm or "elradfmwMT",
        )

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.permit_foreign_addresses = True

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
