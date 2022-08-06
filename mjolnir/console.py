import sys
from argparse import ArgumentParser
from collections import namedtuple

from mjolnir import commands, config

Command = namedtuple('Command', ['name', 'description', 'arguments'])

COMMANDS = [
    Command(
        name='db',
        description='Initialize, load, or update local UniProt database.',
        arguments=[
            (['--location', '-l'], {
                'help': 'Specify path to local database, for initialization or loading data. '
                        'The default location is ./mjolnir_db/prot.db',
                'default': './mjolnir_db/prot.db',
            }),
            (['--init'], {
                'help': 'Initialize a new empty local database. Exit if one already exists. '
                        'If no location is specified, the default location will be chosen.',
                'action': 'store_true',
                'default': False,
            }),
            (['--init-force'], {
                'help': 'Initialize a new empty local database. If one already exists, it will be overwritten.',
                'action': 'store_true',
                'default': False,
            }),
            (['--load'], {
                'help': 'Load UniProtKB data into local database from XML (or xml.gz) files. '
                        'Argument: path(s) to XML file(s).',
                'type': str,
                'nargs': '+',
                'default': None,
            }),
            (['--start'], {
                'help': 'No. of entry to start loading from. Will skip the first N-1 entries. '
                        'Counts from 1.',
                'type': int,
                'default': 0,
            }),
            (['--end'], {
                'help': 'No. of entry to stop loading at. Will load only up to the Nth entry.',
                'type': int,
                'default': None,
            }),
            (['--build-index'], {
                'help': 'Build indices for local database, without loading data.',
                'action': 'store_true',
                'default': False,
            })
        ],
    ),
    Command(
        name='process',
        description='Process local UniProtKB database to calculate protein alignments, '
                    'and coevolution matrices.',
        arguments=[
            (['--location', '-l'], {
                'help': 'Path to the entry database being queried. '
                        f'The default location is {config["default_entry_db_location"]}. '
                        f'Only needed when running --prepare-env',
                'default': config["default_entry_db_location"],
            }),
            (['--env'], {
                'help': 'Path to the processing environment directory.',
                'default': config["default_proc_env_location"],
            }),
            (['--init-env'], {
                'help': 'Prepare the processing environment directory.',
                'action': 'store_true',
                'default': False,
            }),
            (['--run'], {
                # options: hhblits, hhfilter, ccmpred
                'help': 'Run the specified algorithm(s) on the database. '
                        'Available options: all, hhblits, hhfilter, ccmpred.',
                'type': str.casefold,
                'nargs': '+',
                'default': None,
                'choices': ['all', 'hhblits', 'hhfilter', 'ccmpred'],
            }),
            (['--cpu-count'], {
                'help': 'Number of logical CPU cores to use for processing. '
                        'Uses all available if not specified. (only needed for HHBlits)',
                'type': int,
                'default': None,
            }),
            (['--clustdb'], {
                'help': 'Path to the clustering database used by HHBlits. '
                        'Should point to directory containing the clustering ffindex / ffdata files. '
                        'Either in `/path/to/db/` or `/path/to/db/UniRef30_2022_02` format. '
                        'If not specified, the the $CLUSTDB environmental variable is used. '
                        'More info here: https://github.com/soedinglab/hh-suite',
                'default': None,
            }),
            (['--gpu-count'], {
                'help': 'Number of GPU cores to use for processing. '
                        'Uses all available if not specified. (only needed for CCMpred)',
                'type': int,
                'default': None,
            }),
            (['--max-time'], {
                'help': 'Maximum time as "HH:MM:SS" to process. Starts shutdown 1 hour before the time.',
                'type': str,
                'default': None,
            })
        ],
    ),
]

command_name_list = ','.join([cmd.name for cmd in COMMANDS])

help_msg_format = [
    'mjolnir: a tool for protein sequence analysis',
    f'usage: mjolnir <{command_name_list}> -h / [<args>]',
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
    # config.load()  # todo uncomment

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
