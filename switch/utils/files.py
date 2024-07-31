import os

import click


def filter_files(files):
    for file in map(os.path.realpath, files):
        if not os.path.exists(file):
            click.echo("file {file} does not exists".format(file=file), err=True)
        else:
            yield file


def expand_files(*paths):
    for path in filter_files(paths):
        if os.path.isdir(path):
            yield from os.scandir(path)
        else:
            yield path
