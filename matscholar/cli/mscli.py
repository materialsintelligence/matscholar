#!/usr/bin/env python
# Copyright (c) Matscholar Development Team.
# Distributed under the terms of the MIT License.

from __future__ import print_function, unicode_literals

import click
from matscholar.cli.mscli_config import set_config
from matscholar.collect import ScopusCollector
from tabulate import tabulate
from operator import itemgetter

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
            'message': 'What is your full name? ',
        },
        {
            'type': 'input',
            'name': 'MATSCHOLAR_TEXT_MINING_KEY',
            'message': 'Enter your Scopus API text mining key '
                       '(obtained at https://dev.elsevier.com/apikey/manage ) : ',
        },
        {
            'type': 'input',
            'name': 'MATSCHOLAR_HOST',
            'message': 'Enter the hostname of the Matscholar DB: ',
        },
        {
            'type': 'input',
            'name': 'MATSCHOLAR_USER',
            'message': 'Enter your Matscholar username: ',
        },
        {
            'type': 'password',
            'name': 'MATSCHOLAR_PASSWORD',
            'message': 'Enter your Matscholar password: ',
        },
    ]
    answers = {}
    for question in questions:
        answers[question["name"]] = input(question["message"])

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

@click.command("scoreboard")
def scoreboard():
    """See how you rank against the Matscholar contributors.
    """
    collector = ScopusCollector()
    scores = collector.db.build.aggregate([{"$group": {"_id": '$pulled_by', "count": {"$sum": 1}}}])
    print(tabulate(sorted([[e["_id"], e["count"]] for e in scores], key=itemgetter(1), reverse=True),
                   headers=['Name', 'Abstracts Contributed']))

cli.add_command(configure)
cli.add_command(collect)
cli.add_command(scoreboard)

def main():
    cli()
