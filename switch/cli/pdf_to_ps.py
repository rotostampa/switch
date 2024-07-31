import http.client
import os
import urllib.parse

import click
from switch.utils.files import expand_files
from switch.utils.run import grab_and_run
from switch.utils.uuid import uuid7


@click.command(help="Convert pdf to postscript using applescript")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("--unique", is_flag=True, help="Add a unique prefix to the files")
@click.option("--copy", is_flag=True, help="Copy the file instead of moving it")
@click.option("--output", is_flag=True, help="Copy the file instead of moving it")
def pdf_to_ps(files, unique, copy, output):
    raise NotImplementedError


if __name__ == "__main__":
    pdf_to_ps()
