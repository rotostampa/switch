import json
import os
from functools import partial

import click
from switch.utils.run import grab_and_run
from switch.utils.uuid import uuid7

TEMPLATE = """
echo "🚀 Download {url} to temp folder"
curl -f -o ${{TMPDIR}}{operation_id}.temp "{url}" --compressed
echo "📁 Moving file to {destination}"
mv ${{TMPDIR}}{operation_id}.temp "{destination}"
"""


def make_writer(f, name, url, outfolder, base_directory):
    return f.write(
        TEMPLATE.format(
            operation_id=uuid7(),
            name=name,
            url=url,
            destination=os.path.abspath(os.path.join(base_directory, outfolder, name)),
        )
    )


def make_temp_files(json_files, delete, **opts):
    for path in json_files:
        with open(path, "rb") as f:
            for spec in json.load(f):
                yield partial(make_writer, **spec, **opts)

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
    for file in make_temp_files(files, **opts):
        grab_and_run(
            file,
            lambda path, temp, task_id: ("/bin/sh", path),
            task_name="switch_file_download",
            basename="download.sh",
            unique=False,
            copy=False,
            wait_for_result=True,
            cleanup=False,
        )
