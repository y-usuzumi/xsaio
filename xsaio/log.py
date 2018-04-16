import logging

_loggers = {
    'def_log': logging.getLogger("default")
}

for logger_name, logger in _loggers.items():
    globals()[logger_name] = logger


def configure_all_loggers(level=logging.WARNING):
    for logger in _loggers.values():
        logger.setLevel(level)
