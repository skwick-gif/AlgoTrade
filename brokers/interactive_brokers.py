
from ib_insync import IB
from threading import Lock

class IBKRConnector:
	def __init__(self):
		self.ib = IB()
		self.connected = False
		self.account = None
		self.lock = Lock()
		self.last_error = None

	def connect(self, host='127.0.0.1', port=7497, account='', password=None):
		with self.lock:
			try:
				self.ib.disconnect()  # Always disconnect first
			except Exception:
				pass
			try:
				self.ib.connect(host, int(port), clientId=1)
				self.connected = self.ib.isConnected()
				self.account = account
				self.last_error = None
			except Exception as e:
				self.connected = False
				self.last_error = str(e)
		return self.connected

	def disconnect(self):
		with self.lock:
			try:
				self.ib.disconnect()
				self.connected = False
				self.account = None
			except Exception as e:
				self.last_error = str(e)

	def is_connected(self):
		return self.connected

	def get_status(self):
		return {
			'connected': self.connected,
			'account': self.account,
			'error': self.last_error
		}
