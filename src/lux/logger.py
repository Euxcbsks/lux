from logging import Formatter, StreamHandler, getLogger

try:
    import colorlog  # type: ignore
except ImportError:
    colorlog = None

default_fmt = "{asctime} | {levelname:^10} | {name:^10} | {message}"
default_name = "lux"

if colorlog:
    default_handler = colorlog.StreamHandler()
    default_formatter = colorlog.ColoredFormatter("{log_color}" + default_fmt, style="{")
    default_logger = colorlog.getLogger(default_name)
else:
    default_handler = StreamHandler()
    default_formatter = Formatter(default_fmt, style="{")
    default_logger = getLogger(default_name)

default_logger.propagate = False
default_handler.setFormatter(default_formatter)
default_logger.addHandler(default_handler)
