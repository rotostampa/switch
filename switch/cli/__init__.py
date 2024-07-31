import http.client
import os
import pathlib
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.parse
import uuid
from urllib.parse import urlparse

import click
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from switch.cli.ftpserver import ftpserver
from switch.cli.upload import upload


@click.group()
def cli():
    pass


cli.add_command(ftpserver)
cli.add_command(upload)


if __name__ == "__main__":
    cli()
