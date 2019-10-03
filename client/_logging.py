import logging
import logging.config


DEFAULT_LOGGING = {'version': 1, 'disable_existing_loggers': False}

# Strategy here is to create a package-wide logger "scope" that doesn't propagate to the *actual* root
# logger(s). Avoids nastiness with things that do use the root logger, e.g. absl.
_ROOT_LOGGER_NAME = "mathfinder_client"
_pkg_root = logging.getLogger(_ROOT_LOGGER_NAME)


def get_logger_name(name):
    return ".".join([_ROOT_LOGGER_NAME, name])


def get_logger(name):
    return logging.getLogger(get_logger_name(name))


def configure_logging(level=logging.DEBUG, filename=None, filemode=None):
    logging.config.dictConfig(DEFAULT_LOGGING)

    default_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s():%(lineno)s] %(message)s",
        "%d/%m/%Y %H:%M:%S")

    handlers = []
    if not filename:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        console_handler.setFormatter(default_formatter)
        handlers.append(console_handler)
    else:
        file_handler = logging.FileHandler(filename=filename, mode=filemode)
        file_handler.setLevel(level)

        file_handler.setFormatter(default_formatter)
        handlers.append(file_handler)

    _pkg_root.setLevel(level)
    for handler in handlers:
        _pkg_root.addHandler(handler)
    _pkg_root.propagate = False
