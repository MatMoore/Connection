class Observable:
	'''Implement observer pattern'''

	def __init__(self):
		self.listeners = []

	def register_listener(self, listener):
		self.listeners.append(listener) #this object has synasthaesia

	def remove_listener(self, listener):
		try:
			self.listeners.remove(listener)
		except ValueError:
			pass

	def notify(self, *args):
		for i in self.listeners:
			i(args)
