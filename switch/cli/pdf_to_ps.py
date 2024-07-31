import os

import click
from functools import partial
from switch.utils.files import expand_files
from switch.utils.run import grab_and_run
from switch.utils.applescript import applescript_from_template

TEMPLATE = """


tell application "Adobe Acrobat"
    -- Define the input and output paths
    set inputPath to POSIX file {input} as alias
    set outputPath to POSIX path of {output}
    
    -- Open the input PDF document
    open alias inputPath
    
    -- Get the front document (the opened PDF)
    set theDocument to front document
    
    -- Convert to PostScript
    save theDocument to outputPath using PostScript Conversion
    
    -- Close the document
    close theDocument
end tell


"""


def make_applescript(path, temp, task_id, output=None):

    output = os.path.join(output or temp, os.path.basename(path) + ".ps")

    click.echo(output)

    return (
        "/usr/bin/osascript",
        "-e",
        applescript_from_template(
            TEMPLATE,
            input=path,
            output=output
        )
    )


@click.command(help="Convert pdf to postscript using applescript")
@click.argument("files", nargs=-1, type=click.Path())
@click.option(
    "--output", help="Directory where the file should go, defaults to temp directory"
)
@click.option("--unique", is_flag=True, help="Add a unique prefix to the files")
@click.option("--copy", is_flag=True, help="Copy the file instead of moving it")
def pdf_to_ps(files, unique, copy, output):

    for file in expand_files(*files):

        p = grab_and_run(
            file,
            partial(make_applescript, output=output),
            task_name="switch_applescript_postscript",
            unique=unique,
            copy=copy,
        )

        p.wait()
