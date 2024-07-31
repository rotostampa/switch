import click

from importlib import import_module


@click.group()
def cli():
    pass


for module, cmd in (
    ("switch.cli.ftpserver", "ftpserver"),
    ("switch.cli.pdf_to_ps", "pdf_to_ps"),
    ("switch.cli.upload", "upload"),
):

    cli.add_command(getattr(import_module(module), cmd))


if __name__ == "__main__":
    cli()
