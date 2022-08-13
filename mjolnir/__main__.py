import logging
from random import randrange

import os
from datetime import datetime

from mjolnir.console import main


out_dir = 'out'
if not os.path.exists(out_dir):
    os.mkdir(out_dir)

logging.basicConfig(
    encoding='utf-8',
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'{out_dir}/{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.{randrange(1000):0>3}.log'),
        logging.StreamHandler(),
    ],
)

main()
