import json
import requests
from data_logger import rlog
import time
from threading import Thread, Lock
from data_collector import DataCollector
import glob

lock = Lock()

class DataSender:
	def __init__(self):
		self.api_key = 'ANIwBWis.FMgpOhrGLCSBnGPk0YT7rUceTMlI64j4'
		self.headers = {
			'Authorization': f'Api-Key {self.api_key}',
		}
		self.url = 'http://192.168.72.150:8000/api/data_collector'
		self.usb_port = ''
		self.get_usb_port()
		self.data_collector = DataCollector(port=self.usb_port)

	def send(self, data):
		response = requests.post(self.url, json=data, headers=self.headers)
		rlog.info(f'Response status: {response.status_code}, Response text: {response.text}')
		response.raise_for_status()
	
	def get_usb_port(self):
		try:
			ports = glob.glob('/dev/ttyUSB*')
			
			if ports:
				print(f"Found USB ports: {ports}")
				self.usb_port = ports[0]
				return ports[0]
			else:
				raise Exception("No USB ports found.")
		except Exception as e:
			print(f"Failed to get USB port: {e}")
			return None
	
	def collect_data_thread(self):
		while True:
			self.data_collector.collect_curren_inverter_data()
	
	def regular_send_collected_data(self):
		collect_data_thread_th = Thread(target=self.collect_data_thread)
		collect_data_thread_th.start()
		while True:
			try:
				time.sleep(300)
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
					with open('data_to_send.json', 'w') as file:
						file.write(json.dumps(data, indent=4))
					self.send(data)
			except Exception as err:
				rlog.error(err)