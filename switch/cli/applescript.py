import os

import click

from switch.utils.files import expand_files
from switch.utils.run import grab_and_run
from pathlib import Path

from switch.utils.applescript import applescript_from_template






def run_applescript_on_files(template, context_function, files, unique, copy, output):

    for file in expand_files(*files):

        p = grab_and_run(
            file,
            lambda path, temp, task_id: (
                "/usr/bin/osascript",
                "-e",
                applescript_from_template(
                    template,
                    **context_function(
                        path=path,
                        temp=temp,
                        output=output or temp,
                        stem=Path(path).stem,
                    ),
                ),
            ),
            task_name="switch_applescript",
            unique=unique,
            copy=copy,
        )

        p.wait()


TO_POSTSCRIPT = """


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

@click.command(help="Convert pdf to postscript using applescript")
@click.argument("files", nargs=-1, type=click.Path())
@click.option(
    "--output", help="Directory where the file should go, defaults to temp directory"
)
@click.option("--unique", is_flag=True, help="Add a unique prefix to the files")
@click.option("--copy", is_flag=True, help="Copy the file instead of moving it")
def pdf_to_ps(files, unique, copy, output):
    run_applescript_on_files(
        context_function=lambda path, output, stem, **opts: {
            "input": path,
            "output": os.path.join(output, "{}.ps".format(stem)),
        },
        template=TO_POSTSCRIPT,
        files=files,
        unique=unique,
        copy=copy,
        output=output,
    )



DISTILL = """

tell application "Acrobat Distiller"
    -- Define the input and output paths
    set inputPath to POSIX file {input} as alias
    set outputPath to POSIX path of {output}
    
    -- Open the input PDF document
    
    Distill sourcePath inputPath destinationPath outputPath
    
    
end tell

"""

@click.command(help="Distill postscript using applescript")
@click.argument("files", nargs=-1, type=click.Path())
@click.option(
    "--output", help="Directory where the file should go, defaults to temp directory"
)
@click.option("--unique", is_flag=True, help="Add a unique prefix to the files")
@click.option("--copy", is_flag=True, help="Copy the file instead of moving it")
def distill(files, unique, copy, output):
    run_applescript_on_files(
        context_function=lambda path, output, stem, **opts: {
            "input": path,
            "output": output,
        },
        template=DISTILL,
        files=files,
        unique=unique,
        copy=copy,
        output=output,
    )

