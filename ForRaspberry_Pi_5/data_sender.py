import requests
import os
from data_logger import rlog
import time
from threading import Thread, Lock
from data_collector import DataCollector

lock = Lock()

class DataSender:
	def __init__(self):
		self.url = os.getenv('DJANGO_SERVER_URL')
		self.data_collector = DataCollector()

	def send(self, data):
		response = requests.post(self.url, json=data)
		rlog.info(f'Response status: {response.status_code}, Response text: {response.text}')
		response.raise_for_status()  # Перевіряє, чи статус відповіді 200
	
	def collect_data_thread(self):
		while True:
			self.data_collector.collect_curren_inverter_data()
	
	def regular_send_collected_data(self):
		collect_data_thread_th = Thread(target=self.collect_data_thread)
		collect_data_thread_th.start()
		while True:
			try:
				time.sleep(60)
				with lock:
					avg_inv_data = self.data_collector.avg_data()
					inverters_accumulated_data = self.data_collector.inverters_accumulated_data
					inverters_base_config = self.data_collector.inverters_base_config
					inverters_param_states = self.data_collector.inverter_current_parameters
					inverters_errors = self.data_collector.inverters_errors
					data = {
						'avg_inv_data': avg_inv_data,
						'inverters_accumulated_data': inverters_accumulated_data,
						'inverters_base_config': inverters_base_config,
						'inverters_param_states': inverters_param_states,
						'inverters_errors': inverters_errors
					}
					rlog.info(f'----------Data to send-----------\n{data}')
					self.send(data)
			except Exception as err:
				rlog.error(err)