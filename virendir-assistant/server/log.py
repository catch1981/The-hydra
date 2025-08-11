
import logging, os
from logging.handlers import RotatingFileHandler
def get_logger(name="virendir", path="C:/virendir-assistant/var/virendir.log"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers: return logger
    logger.setLevel(logging.INFO)
    h = RotatingFileHandler(path, maxBytes=5_000_000, backupCount=7)
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    h.setFormatter(fmt); logger.addHandler(h); return logger
class TraceAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs): return msg, kwargs
