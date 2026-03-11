import os

import click
from switch.utils.binaries import QPDF
from switch.utils.files import expand_files
from switch.utils.run import grab_and_run


@click.command(help="Optimize PDF files using qpdf")
@click.argument("files", nargs=-1, type=click.Path())
@click.option(
    "--output", help="Directory where the file should go, defaults to temp directory"
)
@click.option("--unique", is_flag=True, help="Add a unique prefix to the files")
@click.option("--copy", is_flag=True, help="Copy the file instead of moving it")
@click.option("--open", "open_out", is_flag=True, help="Open the output folder when done")
def optimize(files, output, unique, copy, open_out):
    for file in expand_files(*files):
        grab_and_run(
            file,
            lambda path, temp, task_id: (
                QPDF,
                path,
                "--linearize",
                "--compress-streams=y",
                "--recompress-flate",
                "--compression-level=9",
                "--normalize-content=y",
                "--optimize-images",
                "--remove-unreferenced-resources=yes",
                "--object-streams=generate",
                "--min-version=1.5",
                os.path.join(
                    temp,
                    os.path.basename(path),
                ),
            ),
            task_name="switch_optimize",
            output=output,
            unique=unique,
            copy=copy,
            open_out=open_out,
        )
