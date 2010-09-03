import multilogger
import wx
from GoGUIWx import GamePanel

class GoApp(wx.App):
	def __init__(self, game_controller, colors):
		self.game_controller = game_controller
		self.colors = colors
		wx.App.__init__(self)

	def OnInit(self):
		'''For now, this will create a game view on startup. Later we will create all the widgets for starting games, and we will create GameViews when games are started.'''
		frame = GamePanel.GamePanel(self.game_controller, self.colors)
		frame.Show(True)
		self.SetTopWindow(frame)
		return True

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
