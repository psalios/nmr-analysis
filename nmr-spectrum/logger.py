import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from config import Properties


def get_logger(filehandler=None, screen_handler=False):

  if filehandler is None:
    if not os.path.exists(Properties.GetProperty("logging.python-server.directory")):
      os.makedirs(Properties.GetProperty("logging.python-server.directory"))
    filehandler = Properties.GetProperty("logging.python-server.directory") + "/" + Properties.GetProperty("logging.python-server.file")
  #Set logging format
  formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

  logger = logging.getLogger()
  loggingLevel = Properties.GetProperty("logging.python-server.level")
  if loggingLevel == "DEBUG":
    logger.setLevel(logging.DEBUG)
  elif loggingLevel == "INFO":
    logger.setLevel(logging.INFO)
  elif loggingLevel == "WARNING":
    logger.setLevel(logging.INFO)
  elif loggingLevel == "ERROR":
    logger.setLevel(logging.INFO)
  elif loggingLevel == "CRITICAL":
    logger.setLevel(logging.INFO)
  else:
    logger.setLevel(logging.NOTSET)

  if filehandler is not None:
    handler = RotatingFileHandler(filehandler, mode='a', maxBytes=10*1024*1024, delay=0, backupCount=1)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

  if screen_handler is not False:
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger.addHandler(screen_handler)

  return logger
