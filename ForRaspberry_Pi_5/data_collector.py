import time
from RS485Client import RS485Client
from data_logger import log

class DataCollector:
	def __init__(self):
		self.client = RS485Client()
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
			'Batt power': {'value': [], 'units': 'W'},
			'Batt current': {'value': [], 'units': 'A'},
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
		while i < 5:
			try:
				receive_data = self.client.get_inverters_data_accept_errors(date_tipe='current_inv_data')
				for key, value in receive_data.items():
					self.current_inv_data[key]['value'].append(value[0])
				time.sleep(10)
			except Exception as err:
				log.error(err)
				time.sleep(10)
		try:
			self.inverters_errors = self.client.get_inverters_data_accept_errors(date_tipe='inverters_errors')
			self.inverters_accumulated_data = self.client.get_inverters_data_accept_errors(date_tipe='inverters_accumulated_data')
			self.inverters_base_config = self.client.get_inverters_data_accept_errors(date_tipe='inverters_base_config')
			self.inverter_current_parameters = self.client.get_inverters_data_accept_errors(date_tipe='inverters_param_states')
		except Exception as err:
			log.error(err)
	
	def avg_data(self):
		
		avg_data = {}
		for key, value in self.current_inv_data.items():
			avg_value = round(sum(value['value']) / len(value['value']), 3)
			avg_data[key] = avg_value
		if len(self.current_inv_data['Battery voltage']['value']) >= 5:
			self.clear_current_inverter_data()
		return avg_data
	