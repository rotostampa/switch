import os

import click
from switch.utils.binaries import MAGICK
from switch.utils.files import expand_files
from switch.utils.run import grab_and_run


@click.command(help="Convert pdf to postscript using applescript")
@click.argument("files", nargs=-1, type=click.Path())
@click.option(
    "--output", help="Directory where the file should go, defaults to temp directory"
)
@click.option("--unique", is_flag=True, help="Add a unique prefix to the files")
@click.option("--copy", is_flag=True, help="Copy the file instead of moving it")
@click.option("--open", "open_out", is_flag=True, help="Open the output folder when done")
def png_to_tiff(files, output, unique, copy, open_out):
    for file in expand_files(*files):
        grab_and_run(
            file,
            lambda path, temp, task_id: (
                MAGICK,
                path,
                "-density",
                "360",
                "-units",
                "PixelsPerInch",
                "-compress",
                "lzw",
                os.path.join(
                    temp,
                    "{}.tiff".format(os.path.splitext(os.path.basename(path))[0]),
                ),
            ),
            task_name="switch_png_to_tiff",
            output=output,
            unique=unique,
            copy=copy,
            cleanup=True,
            open_out=open_out,
        )
