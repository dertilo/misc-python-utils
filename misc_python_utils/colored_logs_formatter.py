import logging


class CustomFormatter(logging.Formatter):
    """
    copypasted from: https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    """

    blue = "\x1b[34;20m"
    # grey = "\x1b[38;20m"
    dark_green = "\x1b[38;5;2m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_: str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )
    # format= '%(name)-12s: %(levelname)-8s %(message)s'
    FORMATS = {  # noqa: RUF012
        logging.DEBUG: blue + format_ + reset,
        logging.INFO: dark_green + format_ + reset,
        logging.WARNING: yellow + format_ + reset,
        logging.ERROR: red + format_ + reset,
        logging.CRITICAL: bold_red + format_ + reset,
    }

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def prepare_logger(
    namespaces: str | list[str] | None = None,
    log_level: int = logging.DEBUG,
    namespaces2loglevel: dict[tuple[str, ...] | str, int] = None,  # noqa: RUF013
) -> None:
    if namespaces2loglevel is None:
        if isinstance(namespaces, str):
            namespaces2loglevel = {(namespaces,): log_level}
        elif isinstance(namespaces, list):
            namespaces2loglevel = {tuple(namespaces): log_level}

    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(ch)
    for logger_names, log_level in namespaces2loglevel.items():
        if isinstance(logger_names, str):
            logger_names = (logger_names,)  # noqa: PLW2901
        for ns in logger_names:
            logger = logging.getLogger(ns)
            logger.setLevel(log_level)
