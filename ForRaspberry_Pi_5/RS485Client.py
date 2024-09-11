from pymodbus.client import ModbusSerialClient
import time
from config import current_inv_data, inverters_errors, inverters_accumulated_data, inverters_base_config, inverters_param_states
from data_logger import log

class RS485Client:
	def __init__(self, port: str = '//dev/ttyUSB0', baudrate: int = 19200, timeout: int = 1):
		self.client = ModbusSerialClient(
			port=port,
			baudrate=baudrate,
			parity='N',
			stopbits=1,
			bytesize=8,
			timeout=timeout,
		)
		self.current_inv_data = current_inv_data
		self.inverters_errors = inverters_errors
		self.inverters_accumulated_data = inverters_accumulated_data
		self.inverters_base_config = inverters_base_config
		self.inverters_param_states = inverters_param_states
		self.connection = None
		self.try_connection_count = 0
	
	def connect(self):
		self.connection = self.client.connect()
	
	def disconnect(self):
		self.client.close()
	
	def send_request(self, address: int, slave: int = 0x04, count: int = 1):
		while self.try_connection_count < 10:
			try:
				self.connect()
				self.try_connection_count = 0
				break
			except Exception as err:
				log.error(err)
				self.try_connection_count += 1
				time.sleep(3)
		if not self.connection:
			return False
		result = self.client.read_holding_registers(address=address, count=count, slave=slave)
		return result.registers[0]
	
	def get_inverters_data_accept_errors(self, date_tipe: str = 'current_inv_data'):
		"""
		Функція для отримання даних через RS485-запит до інвертора. На вхід передається тип даних, який потрібно отримати.
		На вихід отримані дані повертаються у вигляді словника з іменами параметрів і його значеннями.
		:date_tipe: str - 'current_inv_data', 'inverters_accumulated_data', 'inverters_base_config', 'inverters_param_states', 'inverters_errors'
		:return: dictionary
		"""
		data = {}
		config_params_for_requests = {}
		if date_tipe == 'current_inv_data':
			config_params_for_requests = self.current_inv_data
		elif date_tipe == 'inverters_accumulated_data':
			config_params_for_requests = self.inverters_accumulated_data
		elif date_tipe == 'inverters_base_config':
			config_params_for_requests = self.inverters_base_config
		elif date_tipe == 'inverters_param_states':
			return self.get_inverter_param_states()
		elif date_tipe == 'inverters_errors':
			return self.get_inverter_errors()
		for address, value in config_params_for_requests.items():
			param_name = value[0]
			coefficient = value[1]
			units = value[2]
			inverter_response = round(self.send_request(address=int(address)) * coefficient, 3)
			data[param_name] = inverter_response, units
			log.info(f'{param_name}: {inverter_response} {units}')
			time.sleep(0.02)
		return data
	
	def get_inverter_errors(self):
		"""
		Поки не реалізовано, потрібно робити зв'язок з іншою таблицею.
		Тут без помилок на інверторі важко зрозуміти які дані надходять з інвертора
		:return: dict
		"""
		data = {}
		for address, value in self.inverters_errors.items():
			param_name = value[0]
			inverter_response = self.send_request(address=int(address))
			data[param_name] = inverter_response
			log.info(f'{param_name}: {inverter_response}')
			time.sleep(0.02)
		return data
	
	def get_inverter_param_states(self):
		data = {}
		try:
			for address, value in self.inverters_param_states.items():
				param_name = value[0]
				inverter_response = value[1][self.send_request(address=int(address))]
				data[param_name] = inverter_response
				log.info(f'{param_name}: {inverter_response}')
				time.sleep(0.02)
			return data
		except Exception as err:
			log.error(err)
	