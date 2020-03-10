import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import pathlib

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = str(pathlib.Path(__file__).parent.absolute()) + "/logs.txt"

def get_logger(logger_name):
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)

   file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight")
   file_handler.setFormatter(FORMATTER)
   
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG)
   logger.addHandler(console_handler)
   logger.addHandler(file_handler)

   logger.propagate = False
   return logger
