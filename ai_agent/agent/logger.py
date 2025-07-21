import logging
from pathlib import Path

class TreeLineLogger:
    def __init__(self, name: str = "TreeLineLogger", log_to_console: bool = True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "treeline.log"

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        # Optional console handler
        console_handler = None
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            if console_handler:
                self.logger.addHandler(console_handler)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)