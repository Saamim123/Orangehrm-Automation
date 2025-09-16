# utilities/customlogger.py
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional

DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Logs")
DEFAULT_LEVEL = logging.INFO

class CustomLogger:
    """
    Use CustomLogger.get_logger(__name__) across modules.
    Configurable via env vars:
      LOG_DIR, LOG_LEVEL
    """
    @classmethod
    def _ensure_dir(cls, path: str):
        os.makedirs(path, exist_ok=True)

    @classmethod
    def _default_log_file(cls, log_dir: str):
        # single rotating file per run (timestamped name)
        return os.path.join(log_dir, f"automation_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

    @classmethod
    def _create_file_handler(cls, logfile: str, level: int, when: str = "midnight", backup_count: int = 7):
        handler = logging.handlers.TimedRotatingFileHandler(logfile, when=when, backupCount=backup_count, encoding="utf-8")
        handler.setLevel(level)
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s [%(threadName)s] %(message)s")
        handler.setFormatter(fmt)
        return handler

    @classmethod
    def get_logger(cls, name: str = __name__, level: Optional[int] = None, log_dir: Optional[str] = None):
        """
        Returns a configured logger. Safe to call multiple times.
        - name: module name (use __name__ at call site)
        - level: logging level (defaults to env LOG_LEVEL or INFO)
        - log_dir: directory for logs (defaults to ./Logs)
        """
        # resolve config
        level = level or logging.getLevelName(os.environ.get("LOG_LEVEL", "") or DEFAULT_LEVEL)
        if isinstance(level, str):
            level = logging.getLevelName(level)
        log_dir = log_dir or os.environ.get("LOG_DIR") or DEFAULT_LOG_DIR

        cls._ensure_dir(log_dir)
        logfile = cls._default_log_file(log_dir)

        logger = logging.getLogger(name)
        logger.setLevel(level)

        # idempotent - add handlers only if not already configured for this logger
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
            logger.addHandler(ch)

        # add a file handler if not present (we use TimedRotatingFileHandler)
        if not any(isinstance(h, logging.handlers.TimedRotatingFileHandler) for h in logger.handlers):
            fh = cls._create_file_handler(logfile, level)
            logger.addHandler(fh)
            # attach path for convenience (tests can use this)
            logger.log_file_path = logfile

        # avoid double propagation to root logger
        logger.propagate = False
        return logger
