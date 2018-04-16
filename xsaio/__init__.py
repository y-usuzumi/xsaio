import logging

__all__ = ['EPollEventLoop', 'config']

from .event_loop import EPollEventLoop
from .log import configure_all_loggers


def config(**configurations):
    debug = configurations.pop('debug', False)
    if debug:
        configure_all_loggers(logging.DEBUG)
