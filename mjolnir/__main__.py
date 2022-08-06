import logging
from random import randrange

from mjolnir.console import main

logging.basicConfig(
    encoding='utf-8',
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'mjolnir.{randrange(1000):0>3}.log'),
        logging.StreamHandler(),
    ],
)

main()
