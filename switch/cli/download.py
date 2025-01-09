import tempfile

import click
import json
import os
import uuid
from switch.utils.run import grab_and_run

TEMPLATE = """
curl -f -o ${{TMPDIR}}{operation_id}.temp "{url}" --compressed
mv ${{TMPDIR}}{operation_id}.temp "{destination}"
"""

def make_temp_file(name, url, outfolder, base_directory):

    operation_id = uuid.uuid4()

    content = TEMPLATE.format(
        operation_id = operation_id,
        name = name, url = url,
        destination = os.path.abspath(os.path.join(outfolder, base_directory, name))
    )
    print('-'* 20)
    print(content)

    print('-'* 20)
    
    destination = os.path.join(tempfile.gettempdir(), '{}.sh'.format(operation_id))

    with open(destination, 'w') as f:
        f.write(content)

    return destination


def make_temp_files(json_files, delete, **opts):
    for path in json_files:
        with open(path, 'rb') as f:
            for spec in json.load(f):
                yield make_temp_file(**spec, **opts)

        if delete:
            os.path.remove(path)

@click.command(
    help="Download files using a json spec"
)
@click.argument("files", nargs=-1, type=click.Path())
@click.option("--delete", is_flag=True, help="Delete the file after done with it")
@click.option("--outfolder", 'base_directory', help="The base outfolder to download files in", default = '.')
def download(files, **opts):
    for file in make_temp_files(files, **opts):
        grab_and_run(
            file,
            lambda path, temp, task_id: (
                "/bin/sh",
                path,
            ),
            task_name="switch_file_download",
            unique=False,
            copy=False,
            wait_for_result=True,
            cleanup=False,
        )