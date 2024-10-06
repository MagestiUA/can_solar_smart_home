import logging
import os
from logging.handlers import RotatingFileHandler


log_size = 3000 * 1024
log_backup_count = 2
logs_dir = os.path.dirname('logs/')
if not os.path.exists(logs_dir):
	os.makedirs(logs_dir)
def setup_logger(filename):
	logger = logging.getLogger(filename)
	logger.setLevel(logging.INFO)
	file_handler = RotatingFileHandler(filename, maxBytes=log_size, backupCount=log_backup_count, encoding='utf-8')
	file_handler.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger


# log = setup_logger('logs/inverter.log', logging.INFO, encoding='utf-8', max_bytes=log_size, backup_count=log_backup_count)
rlog = setup_logger('logs/requests.log')