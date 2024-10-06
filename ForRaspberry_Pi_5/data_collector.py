import time
from RS485Client import RS485Client
from data_logger import setup_logger

class DataCollector:
	def __init__(self, port: str = ''):
		self.log = setup_logger(f'logs/{port[6:]}.log')
		self.client = RS485Client(port=port, loger=self.log)
		self.current_inv_data = {
			'Battery voltage': {'value': [], 'units': 'V'},
			'Inverter voltage': {'value': [], 'units': 'V'},
			'Grid voltage': {'value': [], 'units': 'V'},
			'BUS voltage': {'value': [], 'units': 'V'},
			'Control current': {'value': [], 'units': 'A'},
			'Inverter current': {'value': [], 'units': 'A'},
			'Grid current': {'value': [], 'units': 'A'},
			'Load current': {'value': [], 'units': 'A'},
			'PInverter': {'value': [], 'units': 'W'},
			'PGrid': {'value': [], 'units': 'W'},
			'PLoad':  {'value': [], 'units': 'W'},
			'Load percent':  {'value': [], 'units': '%'},
			'SInverter': {'value': [], 'units': 'VA'},
			'SGrid': {'value': [], 'units': 'VA'},
			'Sload': {'value': [], 'units': 'VA'},
			'Qinverter': {'value': [], 'units': 'VA'},
			'Qgrid': {'value': [], 'units': 'VA'},
			'Qload': {'value': [], 'units': 'VA'},
			'Inverter frequency': {'value': [], 'units': 'Hz'},
			'Grid frequency': {'value': [], 'units': 'Hz'},
			'AC radiator temperature': {'value': [], 'units': 'C'},
			'Transformer temperature': {'value': [], 'units': 'C'},
			'DC radiator temperature': {'value': [], 'units': 'C'},
			# 'Batt power': {'value': [], 'units': 'W'},
			# 'Batt current': {'value': [], 'units': 'A'},
			'PV voltage': {'value': [], 'units': 'V'},
			'Charger current': {'value': [], 'units': 'A'},
			'Charger power': {'value': [], 'units': 'W'},
		}
		self.inverters_errors = {}
		self.inverters_accumulated_data = {}
		self.inverters_base_config = {}
		self.inverter_current_parameters = {}
	
	def clear_current_inverter_data(self):
		for key, value in self.current_inv_data.items():
			value['value'] = []
	
	def collect_curren_inverter_data(self):
		i = 0
		while i < 30:
			try:
				receive_data = self.client.get_inverters_data_accept_errors(date_tipe='current_inv_data')
				for key, value in receive_data.items():
					self.current_inv_data[key]['value'].append(value[0])
				time.sleep(10)
				i += 1
			except Exception as err:
				self.log.error(err)
				time.sleep(10)
		try:
			self.inverters_errors = self.client.get_inverters_data_accept_errors(date_tipe='inverters_errors')
			time.sleep(1)
			self.inverters_accumulated_data = self.client.get_inverters_data_accept_errors(date_tipe='inverters_accumulated_data')
			time.sleep(1)
			self.inverters_base_config = self.client.get_inverters_data_accept_errors(date_tipe='inverters_base_config')
			time.sleep(1)
			self.inverter_current_parameters = self.client.get_inverters_data_accept_errors(date_tipe='inverters_param_states')
			time.sleep(1)
		except Exception as err:
			self.log.error(err)
	
	def avg_data(self):
		avg_data = {}
		for key, value in self.current_inv_data.items():
			if len(value['value']) > 0:
				avg_value = round(sum(value['value']) / len(value['value']), 2)
				avg_data[key] = avg_value
			else:
				print(f'No data for {key}, value = {value["value"]}')
		if len(self.current_inv_data['Battery voltage']['value']) >= 30:
			self.clear_current_inverter_data()
		return avg_data
	
	def get_cur_data(self):
		return self.client.get_inverters_data_accept_errors(date_tipe='inverters_accumulated_data')

class Collector:
	def __init__(self, port='//dev/ttyUSB1'):
		self.port = port
		self.data_collector = DataCollector(port=port)
	
	def collect_data_thread(self):
		while True:
			self.data_collector.collect_curren_inverter_data()
	
	def print_data(self):
		while True:
			try:
				time.sleep(60)
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
				print(data)
				data_to_print = ''.join(f'{key}: {value}\n' for key, value in data['avg_inv_data'].items())
				data_to_print += ''.join(
					f'{key}: {value}\n' for key, value in data.items() if key != 'avg_inv_data')
			except Exception as err:
				print(err)
			
	def minimal_print(self):
		for key, value in self.data_collector.get_cur_data().items():
			print(f'{key}: {value}')


if __name__ == '__main__':
	from threading import Thread, Lock
	lock = Lock()
	collector1 = Collector(port='//dev/ttyUSB1')
	collector1.minimal_print()

