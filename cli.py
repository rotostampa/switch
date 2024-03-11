import click
import os
import sys
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from urllib.parse import urlparse

@click.group()
def cli():
    pass

def validate_url(ctx, param, value):
    for v in value:
        try:
            parsed_url = urlparse(v, scheme='file')  # Parse the FTP URL

            if parsed_url.scheme.lower() != 'file':
                raise click.BadParameter('Only File URLs are supported. %s' % (parsed_url, ))

            if parsed_url.hostname not in ('localhost', '', None):
                raise click.BadParameter('Only localhost is supported, hostname is %s' % (parsed_url.hostname, ))

        except ValueError:
            raise click.BadParameter('Invalid FILE URL format. It should be in the form "file://user:admin@localhost/path/to/folder"')

        yield parsed_url

@cli.command(help = 'Start an ftp server. Use a list of urls such as file://user:admin@localhost/path/to/folder to define folders')
@click.option('--host', default='0.0.0.0', help='Host IP address to bind to')
@click.option('--port', default=7500, help='Port number to bind to')
@click.option('--perm',  default = None, help='Permission string')
@click.argument('urls', nargs=-1, callback=validate_url)
def ftpserver(host, port, perm, urls):

    authorizer = DummyAuthorizer()

    for url in urls:
        authorizer.add_user(
            url.username or 'admin', 
            url.password or 'admin', 
            url.path or '.', 
            perm=perm or "elradfmwMT"
        )

    handler = FTPHandler
    handler.authorizer = authorizer

    sys.stdout.write(
        (
            "Starting ftp server at {protocol}://{addr}:{port}/\n"
            "Quit the server with {quit_command}.\n"
        ).format(
            protocol="ftp",
            addr=host,
            port=port,
            quit_command="CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C",
        )
    )

    server = FTPServer((host, port), handler)
    server.serve_forever()


if __name__ == '__main__':
    cli()

