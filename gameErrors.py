'''This module defines invalid move exceptions. The ErrorList class is for when multiple errors need to be reported on.'''
class InvalidMove(Exception): pass
class SuicideError(InvalidMove): pass
class KoError(InvalidMove): pass
class NonExistantSquareError(InvalidMove): pass

class ErrorList(Object):
	'''Container for error information. If `ErrorList.errors` is not empty, then there are errors that need handling.'''
	def __init__(self):
		self.errors = []

	def clear(self):
		self.errors = []

	def fail(reason='',detail=''):
		'''Add an error'''
		self.errors.append((reason,detail))

	def __len__(self):
		return len(self.errors)

	def check(self):
		'''Raises an appropriate exception for the first error that occurred, if there were any'''
		if not self.errors: return

		import sys
		reason,detail = self.errors[0]

		try:
			# reason is the name of an exception
			exception = getattr(sys.modules[__name__],reason)
		except:
			# Use a generic exception
			exception = Exception(reason)

		raise exception
