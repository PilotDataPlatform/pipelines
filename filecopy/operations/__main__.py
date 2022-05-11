import logging

from operations.app import app
from operations.commands.copy import copy
from operations.commands.delete import delete

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s\t%(levelname)s\t[%(name)s]\t%(message)s')

    app.add_command(copy)
    app.add_command(delete)
    app()
