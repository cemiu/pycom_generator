import logging

from mjolnir.console import main

logging.basicConfig(
    encoding='utf-8',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO,
)

main()
