import logging
import os
from logging.handlers import RotatingFileHandler

logs_dir = os.path.dirname('logs/')
if not os.path.exists(logs_dir):
	os.makedirs(logs_dir)
def setup_logger(filename, log_level, max_bytes, backup_count, encoding='utf-8'):
	logger = logging.getLogger(filename)
	logger.setLevel(log_level)
	file_handler = RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count, encoding=encoding)
	file_handler.setLevel(log_level)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger


log_size = 3000 * 1024
log_backup_count = 2
log = setup_logger('logs/inverter.log', logging.INFO, encoding='utf-8', max_bytes=log_size, backup_count=log_backup_count)
rlog = setup_logger('logs/requests.log', logging.INFO, encoding='utf-8', max_bytes=log_size, backup_count=log_backup_count)