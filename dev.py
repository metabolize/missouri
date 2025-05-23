#!/usr/bin/env -S poetry run python

import os
import click
from executor import execute


def python_source_files():
    import glob

    include_paths = (
        glob.glob("*.py")
        + glob.glob("missouri/*.py")
        + glob.glob("missouri/**/*.py")
        + ["doc/"]
    )
    exclude_paths = []
    return [x for x in include_paths if x not in exclude_paths]


@click.group()
def cli():
    pass


@cli.command()
def install():
    execute("poetry install --sync")


@cli.command()
def test():
    execute("pytest")


@cli.command()
def coverage():
    execute("pytest --cov=missouri")


@cli.command()
def coverage_report():
    execute("coverage html --fail-under=0")
    execute("open htmlcov/index.html")


@cli.command()
def check_types():
    execute("mypy", "--package", "missouri", "--show-error-codes")


@cli.command()
def lint():
    execute("flake8", *python_source_files())


@cli.command()
def black():
    execute("black", *python_source_files())


@cli.command()
def black_check():
    execute("black", "--check", *python_source_files())


@cli.command()
def doc():
    execute("rm -rf build/ doc/build/ doc/api/")
    execute("sphinx-build -W -b singlehtml doc doc/build")


@cli.command()
def doc_open():
    execute("open doc/build/index.html")


@cli.command()
def publish():
    execute("rm -rf dist/")
    execute("poetry build")
    execute("twine upload dist/*")


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    cli()
