from flask import Flask, request, jsonify
from CAN_Repeater import CANRepeater

app = Flask(__name__)
can = CANRepeater()

@app.route('/send_can', methods=['POST'])
def send_can_message():
	"""
	Приймає JSON з даними для відправки на CAN-шину.
	"""
	try:
		can_id = request.json.get('can_id')
		data = request.json.get('data')
		print(f'Get request {request.json}\nRequest id: {can_id}\nRequest data: {data}')

		if not data or not isinstance(data, list) or len(data) > 8:
			return jsonify({'error': 'Невірний формат даних'}), 400

		try:
			print('Try to send message')
			respond = can.message_repeater(can_id=can_id, data=data, timeout=3)
			print(respond)
			return respond
		except Exception as e:
			return jsonify({'error': str(e)}), 500

	except ValueError:
		return jsonify({'error': 'Невірний CAN ID'}), 400


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
