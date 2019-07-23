#!/usr/bin/env python
# Copyright (c) Matscholar Development Team.
# Distributed under the terms of the MIT License.

from __future__ import print_function, unicode_literals

import click
from PyInquirer import prompt
from matscholar.cli.mscli_config import set_config
from matscholar.collect import ScopusCollector

@click.group()
def cli():
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
                       '(obtained at https://dev.elsevier.com/apikey/manage) ',
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
@click.option('--count', default=1, help='number of blocks')
def contribute(count):
    """Used to contribute data to Matscholar database."""
    collector = ScopusCollector()
    collector.contribute(num_blocks=count)

cli.add_command(configure)
cli.add_command(contribute)

def main():
    cli()

# from matscholar.cli.mscli_config import configure_mscli
# from matscholar.cli.mscli_query import do_query
#
# def main():
#     parser = argparse.ArgumentParser(description="""
#     Welcome to mscli (The materials scholar command line interface)
#     This script works based on several sub-commands with their own options.
#     To see the options for the sub-commands, type "mscli sub-command -h".""")
#
#     subparsers = parser.add_subparsers()
#
#     parser_config = subparsers.add_parser(
#         "set", help="Tool for modifying config variables in .msclirc.yaml configuration file.")
#     groups = parser_config.add_mutually_exclusive_group(required=True)
#     groups.add_argument("-a", "--add", dest="var_spec", nargs="+",
#                         help="Variables to add in the form of space "
#                              "separated key value pairs. E.g., "
#                              "MATSCHOLAR_TEXT_MINING_KEY <api key>")
#     parser_config.set_defaults(func=configure_mscli)
#
#     #TODO: add query on Rester to CLI
#
#
#     parser_collect = subparsers.add_parser(
#         "collect",
#         help="Collect data from the Scopus API and add to the Materials Scholar Database. "
#              "(For internal use by Matscholar collaborators.)")
#
#     group = parser_collect.add_mutually_exclusive_group(required=False)
#     group.add_argument(
#         "-k", "--key", dest="api_key", metavar="format",
#         choices=["poscar", "cif", "cssr"], type=str.lower,
#         help="Get structures from Materials Project and write them to a "
#              "specified format.")
#     group.add_argument(
#         "-e", "--entries", dest="entries", metavar="filename",
#         help="Get entries from Materials Project and write them to "
#              "serialization file. JSON and YAML supported.")
#     group.add_argument(
#         "-d", "--data", dest="data", metavar="fields", nargs="*",
#         help="Print a summary of entries in the Materials Project satisfying "
#              "the criteria. Supply field names to include additional data. "
#              "By default, the Materials Project id, formula, spacegroup, "
#              "energy per atom, energy above hull are shown.")
#     parser_query.set_defaults(func=do_query)
#
#     try:
#         import argcomplete
#         argcomplete.autocomplete(parser)
#     except ImportError:
#         # argcomplete not present.
#         pass
#
#     args = parser.parse_args()
#
#     try:
#         getattr(args, "func")
#     except AttributeError:
#         parser.print_help()
#         sys.exit(0)
#     args.func(args)


if __name__ == "__main__":
    main()
