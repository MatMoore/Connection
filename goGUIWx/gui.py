if __name__=='__main__':
	# Add the parent package modules to the search path
	import sys
	sys.path = ['..'] + sys.path

import multilogger
import wx
from newGameWizard import NewGameWizard

def run():
	'''Start the app and show the new game wizard'''
	app = wx.App()
	wiz = NewGameWizard()
	wiz.Run()
	wiz.Destroy()
	app.SetTopWindow(wiz)
	app.MainLoop()

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)

if __name__ == '__main__':
	info('Starting GUI')
	run()
