
import sys

from argparse import ArgumentParser
from collections import namedtuple
from mjolnir import commands

Command = namedtuple('Command', ['name', 'description', 'arguments'])

COMMANDS = [
    Command(
        name='db',
        description='Initialize, load, or update local UniProt database.',
        arguments=[
            (['--location', '-l'], {
                'help': 'Specify path to local database, for initialization, loading, or updating. '
                        'The default location is ./mjolnir_db/prot.db',
                'default': './mjolnir_db/prot.db',
            }),
            (['--init'], {
                'help': 'Initialize a new empty local database. If no location '
                        'is specified, the default location will be chosen.',
                'action': 'store_true',
                'default': False,
            }),
            (['--load'], {
                'help': 'Load UniProtKB data into local database from an XML file. '
                        'Argument: path to an XML file.',
                'type': str,
                'default': None,
            }),
            (['--update', '-u'], {
                'help': 'Update local database with new data from UniProtKB via the REST API.',
                'action': 'store_true',
                'default': False,
            }),
        ],
    ),
    Command(
        name='process',
        description='Process local UniProtKB database to calculate protein alignments, '
                    'and coevolution matrices.',
        arguments=[
            (['--location', '-l'], {
                'help': 'Path to the local database being queried. '
                        'The default location is ./mjolnir_db/prot.db',
                'default': './mjolnir_db/prot.db',
            }),
            (['--engine'], {
                'help': 'Specify the engine for coevolution generation.',
                'type': str,
                'choices': ['hhblits', 'metapsicov', 'plmdca'],
                'default': 'hhblits',
            }),
            # TODO: FLAGS (CUDA, max seq length, max ram)',
        ],
    ),
    Command(
        name='config',
        description='Create or change configuration.',
        arguments=[
            (['--init'], {
                'help': 'Initialize a new configuration file at ~/.mjolnir/config.ini',
                'action': 'store_true',
                'default': False,
            }),
        ],
    ),
    Command(
        name='env',
        description='Print information about the current environment.',
        arguments=[],
    ),
]

command_name_list = ','.join([cmd.name for cmd in COMMANDS])

help_msg_format = [
    'mjolnir: a tool for protein sequence analysis',
    f'usage: mjolnir <{ command_name_list }> -h / [<args>]',
    'commands:',
]

# print the help message
def print_help():
    help_msg = '\n\n'.join(help_msg_format) + '\n'
    for command in COMMANDS:
        help_msg += '  {}:   \t{}\n'.format(command.name, command.description)

    print(help_msg)


def get_parser():
    description = 'mjolnir: a tool for protein sequence analysis'

    parser = ArgumentParser(prog='mjolnir', description=description)
    # TODO: add version argument

    subparsers = parser.add_subparsers(title='commands')

    for command in COMMANDS:
        sub = subparsers.add_parser(
            command.name,
            description=command.description
        )

        sub.set_defaults(func=commands.__dict__.get(command.name))

        for args, kwargs in command.arguments:
            sub.add_argument(*args, **kwargs)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    if 'func' not in args:
        print_help()
        sys.exit(1)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print('\nInterrupted by user.')
        sys.exit(1)
    # except Exception:
    #     print(traceback.format)
    #     sys.exit(1)
