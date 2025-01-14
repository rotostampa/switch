import os
from pathlib import Path

import click
from switch.utils.applescript import applescript_from_template, raw
from switch.utils.binaries import OSASCRIPT
from switch.utils.files import ensure_dir, expand_files
from switch.utils.run import run


def _ensure_empty(path):
    if os.path.exists(path):
        os.remove(path)
    return path


def echo(c):
    click.echo(c)
    return c


def run_applescript_on_files(template, context_function, files, output):

    for file in expand_files(*files):
        run(
            (
                OSASCRIPT,
                "-e",
                echo(
                    applescript_from_template(
                        template,
                        **context_function(
                            path=file,
                            stem=Path(file).stem,
                            output=ensure_dir(
                                os.path.realpath(output or os.path.dirname(file))
                            ),
                        ),
                    )
                ),
            ),
        )


TO_POSTSCRIPT = """

tell application "Adobe Acrobat"

    close all docs saving no

    -- Define the input and output paths
    set inputPath to POSIX file {pdf} as alias
    set outputPath to POSIX path of {target}

    -- Open the input PDF document
    open alias inputPath


    -- Get the file alias of the opened document
    set inputPathPOSIX to POSIX path of inputPath

    -- Iterate through all open documents to find the matching one
    repeat with doc in documents
        -- Get the file alias of the current document
        set docPath to file alias of doc
        set docPathPOSIX to POSIX path of docPath

        -- Check if the paths match
        if docPathPOSIX is equal to inputPathPOSIX then
            -- Found the matching document, set it to a variable

            -- Convert to PostScript
            save doc to outputPath using {format} Conversion

            exit repeat -- Exit the loop once the matching document is found
        end if


    end repeat

    close all docs saving no

    activate

    tell application "System Events"
        keystroke "w" using command down
        keystroke "w" using command down
        keystroke "w" using command down
    end tell




end tell



"""


@click.command(help="Convert pdf to postscript using applescript")
@click.argument("files", nargs=-1, type=click.Path())
@click.option(
    "--output", help="Directory where the file should go, defaults to temp directory"
)
@click.option("--eps", is_flag=True, help="Export as eps")
def pdf_to_ps(files, output, eps):
    return run_applescript_on_files(
        context_function=lambda path, output, stem, **opts: {
            "pdf": path,
            "target": _ensure_empty(
                os.path.join(output, "{}.{}".format(stem, eps and "eps" or "ps"))
            ),
            "format": raw(eps and "EPS" or "Postscript"),
        },
        template=TO_POSTSCRIPT,
        files=files,
        output=output,
    )


DISTILL = """

tell application "Acrobat Distiller"
    -- Define the input and output paths
    set inputPath to POSIX file {postscript} as alias
    set outputPath to POSIX path of {folder}

    -- Open the input PDF document

    with timeout of 900000 seconds
        Distill sourcePath inputPath destinationPath outputPath
    end timeout

end tell

"""


@click.command(help="Distill postscript using applescript")
@click.argument("files", nargs=-1, type=click.Path())
@click.option(
    "--output", help="Directory where the file should go, defaults to temp directory"
)
def distill(files, output):
    return run_applescript_on_files(
        context_function=lambda path, output, stem, **opts: {
            "postscript": path,
            "folder": output,
        },
        template=DISTILL,
        files=files,
        output=output,
    )
