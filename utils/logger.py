import logging
from pathlib import Path
from config.config_loader import config_load

class LoggerFactory:

    """
    This class help us track the logs of any module that we want for organized logging
    """

    def __init__(self):

        self.config = config_load()
        self.log_path = Path(__file__).resolve().parents[1] / self.config.get("logging").get("log_path")
        self.log_path.mkdir(parents=True, exist_ok=True)
    
    def get_logger(self, module_name: str, level=logging.INFO):

        logger = logging.getLogger(module_name)

        # check if there are already esxisting log handlers
        if logger.handlers:
            return logger
        
        # create a log format we wanted
        formatter = logging.Formatter(
                        fmt="%(asctime)s | %(levelname)-8s | %(name)s | "
                            "%(module)s:%(funcName)s:%(lineno)d | %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S"
                    )
        
        # give a path to capture your log
        module_path = self.log_path / f"{module_name}.log"

        # set the level of logs you want
        logger.setLevel(level)
        
        # create a file handler and the set the formatter you added in the previous step
        module_handler = logging.FileHandler(module_path)
        module_handler.setFormatter(formatter)
        # Add the log handler to your logger
        logger.addHandler(module_handler)

        return logger