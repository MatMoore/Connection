if __name__=='__main__':
	# Add the parent package modules to the search path
	import sys
	sys.path = ['..'] + sys.path

import wx
import wx.wizard
import GamePanel
import controller
import multilogger
import geometry
import board

class NewGameWizard(wx.wizard.Wizard):
	def __init__(self):
		wx.wizard.Wizard.__init__(self, None, -1)
		self.gameType = GameTypePage(self)
		self.players = PlayerPage(self)
		self.board = BoardPage(self)
		self.rules = RulesPage(self)
		self.Bind(wx.wizard.EVT_WIZARD_FINISHED, self.Finish)

	def Run(self):
		'''Show each options screen sequentially, starting with players'''
		self.Link(self.players, self.board)
		self.Link(self.board, self.rules)
		self.RunWizard(self.players)

	def QuickStart(self):
		'''Allow the user to pick from predefined game types'''
		self.RunWizard(self.gameType)

	def Link(self, page1, page2):
		self.UnlinkRight(page1)
		self.UnlinkLeft(page2)
		page1.next = page2
		page2.prev = page1

	def UnlinkRight(self, page):
		if page.next:
			page.next.prev = None
			page.next = None
	
	def UnlinkLeft(self, page):
		if page.prev:
			page.prev.next = None
			page.prev = None

	def Finish(self,event):
		# Read game setup from the wizard pages
		size = self.board.Size()
		info('Size is '+str(size))

		grid = geometry.FoldedGrid(size[0],size[0],1,[('N','S'),('E','W')])

		#Create game controller
		game_controller = controller.Controller()
		black = game_controller.add_local_player('black','Black player')
		white = game_controller.add_local_player('white','White player')
		game_controller.begin_game(board.Board(grid))

		# Show the game in a new window
		colors = {black:(0,0,0), white:(200,200,200)}
		frame = GamePanel.GamePanel(game_controller, colors)
		frame.Show()


class GenericPage(wx.wizard.PyWizardPage):
	'''Subclass of wizard page which allows setting the order of the pages dynamically (unlike WizardPageSimple, which requires the order to be known when the page is created)'''
	def __init__(self,parent,title):
		wx.wizard.PyWizardPage.__init__(self, parent)
		padding = 5
		self.next = self.prev = None
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		title = wx.StaticText(self, -1, title)
		title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
		self.sizer.AddWindow(title, 0, wx.ALIGN_LEFT|wx.ALL, padding)
		self.sizer.AddWindow(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, padding)
		self.SetSizer(self.sizer)

	def GetNext(self):
		return self.next

	def GetPrev(self):
		return self.prev

class GameTypePage(GenericPage):
	'''Choose from predefined game types or pick a custom one'''
	def __init__(self, parent):
		GenericPage.__init__(self,parent,'Choose a game type')

class PlayerPage(GenericPage):
	'''Add the players'''
	def __init__(self, parent):
		GenericPage.__init__(self,parent,'Player set up')

class BoardPage(GenericPage):
	'''Choose the board'''
	def __init__(self, parent):
		GenericPage.__init__(self,parent,'Choose a board')
		self.sc = SizeChooser(self)
		self.sizer.Add(self.sc)

	def Size(self):
		return self.sc.Size()

class RulesPage(GenericPage):
	'''Choose the ruleset, komi, handicap etc'''
	def __init__(self, parent):
		GenericPage.__init__(self,parent,'Game rules')

class SizeChooser(wx.RadioBox):
	'''Pick the board size from a list'''
	def __init__(self, parent):
		self.sizes = [(9,9), (13,13), (19,19)]
		wx.RadioBox.__init__(
			self,
			parent,
			label='Board Size',
			choices=['x'.join(map(str,i)) for i in self.sizes]
		)

		self.choice = 0
		self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, self)

	def EvtRadioBox(self, event):
		self.choice = event.GetInt()

	def Size(self):
		return self.sizes[self.choice]

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)

if __name__ == '__main__':
	app = wx.App()
	wiz = NewGameWizard()
	wiz.Run()
	wiz.Destroy()
	app.SetTopWindow(wiz)
	app.MainLoop()
