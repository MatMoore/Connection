import logging
import sys

def setup():
	'''Use the appropriate log level for the command line args supplied'''
	logging.basicConfig(level=logging.DEBUG)

def logFunctions(module):
	setup()

	if module == '__main__':
		logger = logging.getLogger()
	else:
		logger = logging.getLogger(module)

	return (logger.debug,logger.info,logger.warning,logger.error)
