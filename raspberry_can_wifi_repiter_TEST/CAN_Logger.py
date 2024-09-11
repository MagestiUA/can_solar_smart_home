from logging.handlers import RotatingFileHandler
import logging
import os


logging.basicConfig(level=logging.INFO)
logs_dir = os.path.dirname('logs/')
if not os.path.exists(logs_dir):
	os.makedirs(logs_dir)
log_size = 300 * 1024
log_backup_count = 2
encoding = 'utf-8'
	
def setup_logger(filename: str = 'CAN_Logger.log'):
	filename = os.path.join(logs_dir, filename)
	logger = logging.getLogger(filename)
	logger.setLevel(logging.INFO)
	file_handler = RotatingFileHandler(filename, maxBytes=log_size, backupCount=log_backup_count, encoding=encoding)
	file_handler.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)
	return logger
