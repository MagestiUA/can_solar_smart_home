import json
import can
import os
from CAN_Logger import setup_logger

class CANRepeater:
	def __init__(self):
		self.can_bus = None
		os.system('sudo ifconfig can0 down')
		self.logger = setup_logger(filename='CAN_Logger.log')
		self.logger.info('Start CAN repeater')
	
	def message_repeater(self, can_id, data, timeout=3):
		"""
		Відправляє повідомлення на CAN-шину і отримує відповіді до тих пір, поки не отримано повторне повідомлення з тим самим response_id.

		:param can_id: ID повідомлення CAN.
		:param data: Дані для відправки.
		:param timeout: Час очікування на відповідь (у секундах).
		:return: JSON відповідь або повідомлення про помилку.
		"""
		try:
			self.start()
			self.logger.info(f'Receive params: can_id={can_id}, data={data}, timeout={float(timeout)}')
			if isinstance(data, list) and len(data) <= 8:
				msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
				self.logger.info(f'Send message: {msg}')
			else:
				self.logger.error(f'Invalid data format, Data = {type(data)}, {data}')
				return json.dumps({'error': 'Invalid data format.'})
			
			# Відправляємо повідомлення
			try:
				self.can_bus.send(msg)
			except can.CanError as e:
				return json.dumps({'error': 'Message sending failed', 'details': str(e)})
			
			# Отримання повідомлень з перевіркою на дублікати по response_id
			resp = {}
			try:
				while True:
					response = self.can_bus.recv(timeout)
					if response is None:
						break  # Якщо немає повідомлень протягом тайм-ауту, виходимо з циклу
					
					response_id_hex = hex(response.arbitration_id)
					
					# Якщо response_id вже є в словнику, припиняємо цикл
					if response_id_hex in resp:
						self.logger.info(
							f'Duplicate message detected, stopping reception. response_id = {response_id_hex}')
						break
					
					self.logger.info(
						f'response_id = {response.arbitration_id}, data = {response.data}, time = {response.timestamp}')
					
					# Додаємо повідомлення в словник
					resp[response_id_hex] = dict(
						data=list(response.data),  # Перетворюємо байти в список для JSON
						time=response.timestamp
					)
			except can.CanError as e:
				return json.dumps({'error': 'Message reception failed', 'details': str(e)})
			
			return json.dumps(resp) if resp else json.dumps({'status': 'No response received'})
		except Exception as e:
			return json.dumps({'error': 'Message sending/receiving failed', 'details': str(e)})
		finally:
			self.shutdown()

	def start(self):
		os.system('sudo ip link set can0 type can bitrate 100000')
		os.system('sudo ifconfig can0 up')
		self.can_bus = can.interface.Bus(channel='can0', interface='socketcan')
		
	def shutdown(self):
		"""Закриття CAN інтерфейсу"""
		if self.can_bus:
			self.can_bus.shutdown()  # Закриваємо об'єкт CAN-шини
		os.system('sudo ifconfig can0 down')
