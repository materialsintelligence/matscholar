#!/usr/bin/env python
# Copyright (c) Matscholar Development Team.
# Distributed under the terms of the MIT License.

from __future__ import print_function, unicode_literals

import click
from questionary import prompt
from matscholar.cli.mscli_config import set_config
from matscholar.collect import ScopusCollector

@click.group()
def cli():
    """ Welcome to the Matscholar Command Line Interface! To use this cli,
    configure your settings with `mscli configure` and then contribute abstracts
    to the project with `mscli contribute` (note: this is only for internal
    collaborators.)
    """
    pass

@click.command("configure")
def configure():
    """Used to configure Matscholar configuration settings."""

    questions = [
        {
            'type': 'input',
            'name': 'MATSCHOLAR_NAME',
            'message': 'Whate is your full name?',
        },
        {
            'type': 'input',
            'name': 'MATSCHOLAR_TEXT_MINING_KEY',
            'message': 'Enter your Scopus API text mining key '
                       '(obtained at https://dev.elsevier.com/apikey/manage ) ',
        },
        {
            'type': 'input',
            'name': 'MATSCHOLAR_HOST',
            'message': 'Enter the hostname of the Matscholar DB',
        },
        {
            'type': 'input',
            'name': 'MATSCHOLAR_USER',
            'message': 'Enter your Matscholar username',
        },
        {
            'type': 'password',
            'name': 'MATSCHOLAR_PASSWORD',
            'message': 'Enter your Matscholar password',
        },
    ]

    answers = prompt(questions)
    set_config(answers)

@click.command("contribute")
@click.option('--count', default=1, help='number of blocks (default is 1)')
def collect(count):
    """Used to contribute data to Matscholar database.
    Args:
        count (int): Number of blocks to process before exiting.
    """
    collector = ScopusCollector()
    collector.collect(num_blocks=count)

cli.add_command(configure)
cli.add_command(collect)

def main():
    cli()
