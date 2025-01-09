from functools import partial
from importlib import import_module
from switch.utils.files import ensure_dir

import click
import os
import switch
import tempfile
import threading
import time


def lock_path(lock, basedir=os.path.join(os.path.dirname(switch.__file__), "locks")):
    return os.path.join(ensure_dir(basedir), "{}.lock".format(lock))


def acquire_lock(lock, wait_time=0.3, retry_time=0.1):

    path = lock_path(lock)

    with tempfile.NamedTemporaryFile("w", delete=False) as t:

        while True:

            t.seek(0)
            t.write(str(time.time()))

            try:
                os.link(t.name, path)
                break
            except FileExistsError:
                pass

            with open(path) as f:

                try:
                    lock_time = float(f.read())
                except ValueError:
                    print("file was full of garbage, using creation time")
                    lock_time = os.path.getctime(path)

                if lock_time + wait_time <= time.time():
                    print("lock is expired")
                    break
                else:
                    print("acquiring file failed", lock_time, time.time())

            time.sleep(retry_time)

        print("acquired")

        return t.name


def update_lock(temp, lock, update_time=0.1):

    path = lock_path(lock)

    with open(temp, "w") as t:
        while os.path.exists(path):
            t.seek(0)
            t.write(str(time.time()))
            time.sleep(update_time)


def release_lock(thread, temp, lock):

    path = lock_path(lock)

    if os.path.exists(path):
        os.remove(path)
    thread.join()
    if os.path.exists(temp):
        os.remove(temp)


@click.group()
@click.pass_context
@click.option(
    "--lock", help="Enable lock that writes timestamp to file every 0.1 seconds."
)
def cli(ctx, lock):

    if lock:

        temp = acquire_lock(lock=lock)

        # Create and start the thread
        thread = threading.Thread(
            target=update_lock, kwargs={"temp": temp, "lock": lock}
        )
        thread.daemon = True
        thread.start()

        ctx.call_on_close(partial(release_lock, temp=temp, thread=thread, lock=lock))


for module, cmd in (
    ("switch.cli.ftpserver", "ftpserver"),
    ("switch.cli.applescript", "pdf_to_ps"),
    ("switch.cli.applescript", "distill"),
    ("switch.cli.upload", "upload"),
    ("switch.cli.download", "download"),
    ("switch.cli.noop", "wait"),
    ("switch.cli.magick", "png_to_tiff"),
):

    cli.add_command(getattr(import_module(module), cmd))


if __name__ == "__main__":
    cli()
