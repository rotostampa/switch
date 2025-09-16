import json
import os

import click
from switch.utils.binaries import CURL
from switch.utils.run import run


def get_download_destination(name, outfolder, base_directory, url = None, mirrors = None):
    destination = os.path.abspath(os.path.join(base_directory, outfolder, name))

    if not os.path.exists(os.path.dirname(destination)):
        raise Exception(f"Directory {os.path.dirname(destination)} does not exist")

    urls = []

    if url:
        urls.append(url)

    if mirrors:
        urls.extend(mirrors)

    return urls, destination


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
    for mirrors, destination in read_json_files(files, **opts):
        success = False
        for url in mirrors:
            process = run((CURL, "-f", "-o", destination, url, "--compressed"), wait_for_result=True)
            if process.returncode == 0:
                click.echo(f"Succesfully downloaded from {url}")
                success = True
                break
            else:
                click.echo(f"Failed to download from {url}: curl returned {process.returncode}")

        if not success:
            click.echo(f"Failed to download to {destination} from all mirrors")
