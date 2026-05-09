import logging

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S',
        level=level
    )
