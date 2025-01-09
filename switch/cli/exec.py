import tempfile

import click
import json
import os
import uuid
from switch.utils.run import grab_and_run

@click.command(
    help="Exec script files"
)
@click.argument("files", nargs=-1, type=click.Path())
@click.option("--unique", is_flag=True, help="Add a unique prefix to the files")
@click.option("--copy", is_flag=True, help="Copy the file instead of moving it")
def exec(files, unique, copy):
    for file in files:
        grab_and_run(
            file,
            task_name="switch_file_exec",
            unique=unique,
            copy=copy,
            wait_for_result=False,
            cleanup=False,
        )