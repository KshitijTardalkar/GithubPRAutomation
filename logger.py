import logging
import os
from logging.handlers import RotatingFileHandler

class AppLogger:
    def __init__(self, name: str, log_dir: str = "logs", log_level=logging.DEBUG):
        os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

            # Console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)

            # Rotating file handler
            fh = RotatingFileHandler(
                os.path.join(log_dir, f"{name}.log"),
                maxBytes=5 * 1024 * 1024,
                backupCount=3
            )
            fh.setLevel(log_level)
            fh.setFormatter(formatter)

            self.logger.addHandler(ch)
            self.logger.addHandler(fh)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)

    def debug(self, msg: str):
        self.logger.debug(msg)
