import logging
import os
from datetime import datetime
from typing import Optional


class COLOR:
    NOCOLOR = "\033[0m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    ORANGE = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHTGRAY = "\033[0;37m"
    DARKGRAY = "\033[1;30m"
    LIGHTRED = "\033[1;31m"
    LIGHTGREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHTBLUE = "\033[1;34m"
    LIGHTPURPLE = "\033[1;35m"
    LIGHTCYAN = "\033[1;36m"
    WHITE = "\033[1;37m"


def create_date_path() -> str:
    """
    Create a date-based path string.

    Returns:
        str: A string representing the current date path in the format 'year/month/day'.
    """
    now = datetime.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    return os.path.join(year, month, day)


class CustomFormatter(logging.Formatter):
    def __init__(self, format_log, format_log_timer):
        super().__init__()
        self.format_log = format_log
        self.format_log_timer = format_log_timer

    def select_format(self, format_type):
        return {
            logging.DEBUG: COLOR.LIGHTBLUE + format_type + COLOR.NOCOLOR,
            logging.INFO: COLOR.LIGHTCYAN + format_type + COLOR.NOCOLOR,
            logging.WARNING: COLOR.YELLOW + format_type + COLOR.NOCOLOR,
            logging.ERROR: COLOR.RED + format_type + COLOR.NOCOLOR,
            logging.CRITICAL: COLOR.PURPLE + format_type + COLOR.NOCOLOR,
        }

    def format(self, record):
        format_type = self.format_log_timer if "_timer.py" in record.pathname else self.format_log
        FORMATS = self.select_format(format_type)
        log_fmt = FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of Logger exists."""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        name: str = "shift",
        level: int = logging.DEBUG,
        path_file: Optional[str] = None,
        root_log: str = "logs",
        format_log: str = "%(asctime)s - %(levelname)s - [in %(pathname)s:%(lineno)d] - %(message)s",
        format_log_timer: str = "%(asctime)s - %(levelname)s - [Timer] - %(message)s",
    ):
        """
        Initialize logger. Only initializes once, subsequent calls return the existing instance.

        Args:
            name (str): Name of the logger.
            level (str): Level of the logger.
            path_file (str): Path to the log file.
            format_log (str): Format of the log record.

        Attributes:
            logger (logging.Logger): Logger object.

        """
        # Only initialize once
        if self._initialized:
            return

        self.name = name
        self.level = level
        self.path_file = path_file

        self.format_log = format_log
        self.format_log_timer = format_log_timer
        self.format = CustomFormatter(self.format_log, self.format_log_timer)
        self.root_log = root_log

        self.logger = logging.getLogger(self.name)
        self.configure()

        self._initialized = True

    def create_log_file(self):
        self.root_log = os.path.join(self.root_log, create_date_path())
        os.makedirs(self.root_log, exist_ok=True)
        return os.path.join(self.root_log, self.path_file)

    def configure(self):
        """Configures the logger."""
        # Remove Handlers if it exist to handle duplicate log
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        if self.logger.level == 0 or self.level < self.logger.level:
            self.logger.setLevel(self.level)

        if len(self.logger.handlers) == 0:
            handler = logging.StreamHandler()
            handler.setLevel(self.level)
            handler.setFormatter(self.format)
            self.logger.addHandler(handler)

        if self.path_file:
            self.path_file = self.create_log_file()
            path_file_handler = logging.FileHandler(self.path_file)
            path_file_handler.setLevel(self.level)
            path_file_handler.setFormatter(logging.Formatter(self.format_log))
            self.logger.addHandler(path_file_handler)

        self.logger.propagate = False


# Init logger
logger_name = "lecturehub-chatbot"
logger = Logger(name=logger_name, path_file=f"{logger_name}.log").logger
