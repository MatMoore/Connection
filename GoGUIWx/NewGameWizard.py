if __name__=='__main__':
	# Add the parent package modules to the search path
	import sys
	sys.path = ['..'] + sys.path

import wx
import wx.wizard
import GamePanel
import controller

class NewGameWizard(wx.wizard.Wizard):
	def __init__(self):
		wx.wizard.Wizard.__init__(self, None, -1)
		self.controller = None
		self.gameType = GameTypePage(self)
		self.players = PlayerPage(self)
		self.board = BoardPage(self)
		self.rules = RulesPage(self)

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

class RulesPage(GenericPage):
	'''Choose the ruleset, komi, handicap etc'''
	def __init__(self, parent):
		GenericPage.__init__(self,parent,'Game rules')

if __name__ == '__main__':
	app = wx.App()
	wiz = NewGameWizard()
	wiz.Run()
	wiz.Destroy()
	app.SetTopWindow(wiz)
	app.MainLoop()
