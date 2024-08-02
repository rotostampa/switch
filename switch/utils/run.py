from switch.utils.uuid import uuid7
import click
import os
import shutil
import subprocess
import sys
import tempfile


def _screen(path, temp, task_id):
    return [
        "/opt/homebrew/bin/screen",
        "-L",
        "-Logfile",
        os.path.join(temp, "screen.log"),
        "-S",
        "cmd-{task_id}".format(task_id=task_id),
        "-dm",
        "/bin/sh",
        path,
    ]


def file_to_temp_dir(source, task_name, unique=False, copy=False):
    task_id = uuid7()

    # Create a temporary directory with the UUID name
    temp_dir = os.path.join(tempfile.gettempdir(), task_name, str(task_id))
    os.makedirs(temp_dir)

    # Define the destination file path
    dest = os.path.join(
        temp_dir,
        unique
        and "{uuid}-{basename}".format(uuid=uuid7(), basename=os.path.basename(source))
        or os.path.basename(source),
    )

    # Move the file to the new directory

    if copy:
        shutil.copy(source, dest)
    else:
        shutil.move(source, dest)

    return (dest, temp_dir, task_id)


def run(args, wait_for_result=False):
    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=os.environ,
    )
    if wait_for_result:
        p.wait()
    return p


def grab_and_run(
    file,
    builder=_screen,
    task_name="switch_task_run",
    wait_for_result=False,
    cleanup=False,
    **opts,
):
    path, temp, task_id = file_to_temp_dir(file, task_name, **opts)

    click.echo("Running {path}".format(path=path))

    p = run(builder(path, temp, task_id), wait_for_result=wait_for_result)

    if cleanup:
        shutil.rmtree(temp)

    return p
