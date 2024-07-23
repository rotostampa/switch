from huey import SqliteHuey
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from urllib.parse import urlparse
from watchdog.events import LoggingEventHandler
from watchdog.observers import Observer
import click
import os
import subprocess
import shutil
import sys
import tempfile
import time
import uuid


@click.group()
def cli():
    pass


# WORKER LOGIC


huey = SqliteHuey(filename=os.path.join(os.path.dirname(__file__), "huey.db"))


@huey.task()
def run_script(temp, args):
    # Open the log file in write mode

    stderr = os.path.join(temp, "stderr.txt")
    stdout = os.path.join(temp, "stdout.txt")

    with open(stderr, "w") as stdout_file:
        with open(stdout, "w") as stdout_file:
            # Run the script using /bin/sh

            click.echo(
                "{temp} started".format(temp=temp),
                err=True,
            )
            result = subprocess.run(args, stdout=stdout_file, stderr=stdout_file)
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


def file_to_temp_dir(source, task_name, name=None, delete = True):

    # Create a temporary directory with the UUID name
    temp_dir = os.path.join(tempfile.gettempdir(), task_name, str(uuid.uuid4()))
    os.makedirs(temp_dir)

    # Define the destination file path
    dest = os.path.join(temp_dir, name or os.path.basename(source))

    # Move the file to the new directory

    shutil.copy(source, dest)

    if delete:
        os.remove(source)

    return temp_dir, dest


def filter_files(files):
    for file in map(os.path.realpath, files):
        if not os.path.exists(file):
            click.echo("file {file} does not exists".format(file=file), err=True)
        else:
            yield file


def move_and_run(file):

    click.echo("Running script file {file}".format(file=file))

    temp, path = file_to_temp_dir(file, "switch_task_run")

    run_script.schedule((temp, ["/bin/sh", path]), delay=0)


def move_and_upload(file):

    click.echo("Uploading file {file} to s3".format(file=file))

    temp, path = file_to_temp_dir(
        file, "switch_file_upload", "{}-{}".format(uuid.uuid4(), os.path.basename(file))
    )

    run_script.schedule(
        (
            temp,
            (
                ".venv/bin/aws",
                "s3",
                "cp",
                path,
                "s3://workflow-upload/",
                "--acl",
                "public-read",
            ),
        ),
        delay=0,
    )


class TaskHandler(LoggingEventHandler):

    def __init__(self, file_handler, **opts):
        self.file_handler = file_handler
        super().__init__(**opts)

    def on_created(self, file):
        return self.file_handler(file.src_path)

    def on_moved(self, file):
        return self.file_handler(file.src_path)


@cli.command(help="Starts the task worker")
@click.option("--workers", default=4, help="Number of worker to spawn")
@click.option(
    "--watch", multiple=True, type=click.Path(), help="Folders to watch for changes"
)
@click.option(
    "--upload", multiple=True, type=click.Path(), help="Folders to watch for uploads"
)
def worker(workers, watch, upload, recursive=False):

    for folders, handler in (
        (watch, move_and_run),
        (upload, move_and_upload),
    ):

        if folders := tuple(filter_files(folders)):

            observer = Observer()

            for folder in folders:
                for file in os.scandir(folder):
                    handler(file.path)

            time.sleep(0.01)

            for folder in folders:
                click.echo("Watching folder {folder} for changes".format(folder=folder))
                observer.schedule(TaskHandler(handler), folder, recursive=recursive)

            observer.start()

    click.echo(
        (
            "Starting {workers} workers\n" "Quit the process with {quit_command}.\n"
        ).format(
            workers=workers,
            quit_command="CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C",
        )
    )

    huey.create_consumer(workers=workers).run()


@cli.command(help="Schedule a list of script files for execution")
@click.argument("files", nargs=-1)
def runscript(files):

    for file in filter_files(files):

        move_and_run(file)


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
