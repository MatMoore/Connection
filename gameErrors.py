'''This module defines invalid move exceptions. The ErrorList class is for when multiple errors need to be reported on.'''
class InvalidMove(Exception):
	def __init__(self, errors):
		Exception.__init__(self)
		self.errors = errors

from board import NonExistentPointError,OccupiedError,SizeError
import multilogger

class ErrorList(object):
	'''Container for error information. If `ErrorList.errors` is not empty, then there are errors that need handling.'''
	def __init__(self):
		self.errors = []

	def clear(self):
		self.errors = []

	def fail(self, reason, detail=''):
		'''Add an error'''
		self.errors.append((reason,detail))

	def __len__(self):
		return len(self.errors)

	def check(self):
		'''Raises an exception if errors were encountered.'''
		if not self.errors: return

		raise InvalidMove(self.errors)

debug,info,warning,error = multilogger.logFunctions(__name__)
