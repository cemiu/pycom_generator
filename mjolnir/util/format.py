import textwrap

import re


def human_num(num):
    if num == 1:
        return 'operation'
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def format_bytes(size):
    # 2**10 = 1024
    power = 2 ** 10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power and n < 4:
        size /= power
        n += 1
    return f'{size:.2f}{power_labels[n]}B'


# converts a protein sequence into a FASTA string
seq_to_fasta = lambda seq_id, seq: f'>{seq_id}\n{textwrap.fill(seq, width=60)}\n'


# splits a string along a delimiter, but ignores quoted sections
split = lambda s, delim=' ': re.split(f'''{delim}(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', s)
