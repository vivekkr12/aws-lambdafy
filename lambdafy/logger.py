import logging


def create_logger():
    logger = logging.getLogger('lambdafy')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('lambdafy==> %(asctime)s %(levelname)s: %(message)s', '%Y-%m-%dT%H:%M:%S%z')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


lambdafy_logger = create_logger()
