import json
import os

import click
from switch.utils.binaries import CURL
from switch.utils.run import run


def get_download_destination(name, url, outfolder, base_directory):
    return url, os.path.abspath(os.path.join(base_directory, outfolder, name))


def read_json_files(json_files, delete, **opts):
    for path in json_files:
        with open(path, "rb") as f:
            for spec in json.load(f):
                yield get_download_destination(**spec, **opts)

        if delete:
            os.path.remove(path)


@click.command(help="Download files using a json spec")
@click.argument("files", nargs=-1, type=click.Path())
@click.option("--delete", is_flag=True, help="Delete the file after done with it")
@click.option(
    "--outfolder",
    "base_directory",
    help="The base outfolder to download files in",
    default=".",
)
def download(files, **opts):
    for url, destination in read_json_files(files, **opts):
        run((CURL, "-f", "-o", destination, url, "--compressed"))
