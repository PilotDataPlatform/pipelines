import logging
import logging.handlers
import sys


class Logger:
    def __init__(self, f, console=False, maxBytes=100000000, backupCount=1000):
        self.f = f
        self.logger = None
        self.setup(console, maxBytes, backupCount)

    def setup(self, console, maxBytes, backupCount):
        try:
            # setup the logger
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.INFO)
            handler = logging.handlers.RotatingFileHandler(self.f, maxBytes=maxBytes, backupCount=backupCount)
            formatter = logging.Formatter('%(asctime)s-%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            if console:
                self.logger.addHandler(logging.StreamHandler(sys.stdout))
        except Exception as err:
            raise LoggerException(err)


class LoggerException(Exception):
    pass
