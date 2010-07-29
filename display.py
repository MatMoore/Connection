import game
import board
import pygame
from pygame.locals import *
import geometry
import sys
import observer
import multilogger
import rules
import wx

class GridViewPygame(observer.Observable):
	'''Draw grids using pygame'''

	def __init__(self, grid, surface, scale=None, rotation=0, zoom_to_fit=False, join_connected=False, highlight_connected=True, colors = {}, mainScreen=False, offset=(20,20)):
		observer.Observable.__init__(self)
		grid_width = max([x for x,y in grid.points])
		grid_height = max([y for x,y in grid.points])
		width = surface.get_width()-2*offset[0]
		height = surface.get_height()-2*offset[1]

		if zoom_to_fit:
			scale = min(width/float(grid_width), height/float(grid_height))
		elif scale is None:
			scale = 1

		self.scale = scale
		self.offset = offset
		self.grid = grid
		self.surface = surface
		self.grid.register_listener(self.draw)
		self.highlighted = None

		self.highlight_connected = highlight_connected
		self.join_connected = join_connected

		if colors:
			self.colors = colors
		else:
			self.colors = {
					'black':(0,0,0),
					'white':(255,255,255)
			}

		# Flag to specify if we are drawing to the screen surface
		self.mainScreen = mainScreen
		self.draw()

	def draw(self, *args):
		'''Draw the grid'''
		debug('Redrawing grid')
		scale = self.scale
		self.surface.fill((255,255,255))

		# This actually draws the line for each connection twice but never mind.
		# It also doesn't care about whether edge connections should be visible.
		if self.join_connected:
			for a,bs in self.grid.connections.items():
				for b in bs:
					ax,ay = self.grid_to_view(a)
					bx,by = self.grid_to_view(b)
					pygame.draw.line(self.surface, (0,0,0), (ax,ay), (bx,by),4)

		for p in self.grid.points:
			x,y = p
			value = self.grid.get_point(x,y)
			x,y = self.grid_to_view(p)

			if value is not None and value[0] in self.colors:
				pygame.draw.circle(self.surface, self.colors[value[0]], (int(x),int(y)), 15)
			else:
				pygame.draw.circle(self.surface, (0,0,0), (int(x),int(y)), 5)

		if self.highlight_connected and self.highlighted:
			debug('Highlighting connections for %s' % str(self.highlighted))
			for c in self.grid.connections[self.highlighted]:
				x,y = self.grid_to_view(c)
				pygame.draw.circle(self.surface, (0,255,0), (int(x),int(y)), 2)

		if self.mainScreen:
			pygame.display.flip()

		self.notify()

	def grid_to_view(self,pos):
		'''Convert grid coordinated to view ones'''
		x,y = pos
		ox,oy = self.offset
		return(x*self.scale+ox, y*self.scale+oy)

	def view_to_grid(self, pos):
		'''Convert view coordinates to grid ones'''
		x,y = pos
		ox,oy = self.offset
		x = int(round((x-ox)/self.scale))
		y = int(round((y-oy)/self.scale))
		return (x,y)

	def on_click(self, pos):
		pass

class GameViewPygame(GridViewPygame):
	'''An interactive go board'''
	def __init__(self, game_controller, surface, scale=None, rotation=0, zoom_to_fit=False, join_connected=False, highlight_connected=True, colors = {}):
		GridViewPygame.__init__(self, game_controller.game.board.grid, surface, scale, rotation, zoom_to_fit, join_connected, highlight_connected, colors)
		self.controller = game_controller
		self.accept_moves = game_controller.accept_local_moves

	def on_click(self, pos):
		'''Callback called when the user clicks in the window'''
		# Ignore clicks outside the board
		# TODO: fix board to include all the top/left of stones properly
		x,y = pos

		if x < 0 \
		or y < 0 \
		or x > self.surface.get_width() \
		or y > self.surface.get_height():
			return

		pos = self.view_to_grid(pos)

		if self.controller.accept_local_moves:
			try:
				debug('Playing %s,%s...' % pos)
				self.controller.play_move(pos)
			except game.NotYourTurnError:
				debug('Not your turn')
			except board.BoardError:
				debug('Cannot place a stone there')
			except rules.KoError:
				debug('Invalid move (ko)')
			except rules.SuicideError:
				debug('Invalid move (suicide)')
			except rules.InvalidMove:
				debug('Invalid move')

class GameGUIPygame():
	'''GUI for playing a game of go'''
	def __init__(self,game_controller,screen,board_size,offset,**kwargs):
		self.screen = screen
		board_surface = pygame.Surface(board_size)
		self.game_view = GameViewPygame(game_controller,board_surface,**kwargs)
		self.game_view.register_listener(self.draw)

		b_left,b_top = offset
		b_width,b_height = board_size
		self.layout = {
				'board': (b_left,b_top,b_left+b_width,b_top+b_height)
		}

		self.draw()

	def screen_to_view(self,pos,view='board'):
		'''Convert screen coordinates into coordinates for a view'''
		x,y = pos
		left = self.layout[view][1]
		top = self.layout[view][0]
		return (x-left, y-top)

	def draw(self, *args):
		'''Draw the gui'''
		self.screen.fill((255,255,255))

		# Draw the board in the middle
		board_pos = self.layout['board'][:2]
		self.screen.blit(self.game_view.surface, board_pos)
		pygame.display.flip()

	def on_click(self,pos):
		'''Forward on_click event down to child views'''
		x,y = self.screen_to_view(pos)
		self.game_view.on_click(pos)


class BoardViewWx(wx.Panel):
	'''Show the board using wxPython'''

	def __init__(self, colors, parent=None, id=wx.ID_ANY):
		wx.Panel.__init__(self, parent, id)
		self.colors = colors

	def GridToView(self,pos):
		'''Convert grid coordinated to view ones'''
		x,y = pos
		ox,oy = self.offset
		return(x*self.scale+ox, y*self.scale+oy)

	def ViewToGrid(self, pos):
		'''Convert view coordinates to grid ones'''
		x,y = pos
		ox,oy = self.offset
		x = int(round((x-ox)/self.scale))
		y = int(round((y-oy)/self.scale))
		return (x,y)

	def OnClick(self, pos):
		pass


class PlayableBoardWx(BoardViewWx):
	'''Playable board using wxPython'''
	def __init__(self, controller, colors, parent=None, id=wx.ANY_ID):
		BoardViewWx.__init__(self, colors, parent, id)
		self.controller = controller

	def OnClick(self, pos):
		'''Callback called when the user clicks in the window'''
		# Ignore clicks outside the board
		# TODO: fix board to include all the top/left of stones properly
		x,y = pos

		if x < 0 \
		or y < 0 \
		or x > self.surface.get_width() \
		or y > self.surface.get_height():
			return

		pos = self.ViewToGrid(pos)

		if self.controller.accept_local_moves:
			try:
				debug('Playing %s,%s...' % pos)
				self.controller.play_move(pos)
			except game.NotYourTurnError:
				debug('Not your turn')
			except board.BoardError:
				debug('Cannot place a stone there')
			except rules.KoError:
				debug('Invalid move (ko)')
			except rules.SuicideError:
				debug('Invalid move (suicide)')
			except rules.InvalidMove:
				debug('Invalid move')


class GameViewWx(wx.Frame):
	def __init__(self,game_controller,colors,parent=None,id=wx.ID_ANY,title='Go'):
		wx.Frame.__init__(self,parent,id,title,size=(360,400))
		self.panel = wx.Panel(self, wx.ID_ANY)
		
		self.game_controller = game_controller
#		board = BoardImage(game,self.panel,humanPlayers=localPlayers)
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)
#		mainSizer.Add(board,0,wx.FIXED_MINSIZE)
		
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		passButton = wx.Button(self.panel, wx.ID_ANY, 'Pass')
		resignButton = wx.Button(self.panel, wx.ID_ANY, 'Resign')
		buttonSizer.Add(passButton, 1, wx.ALL|wx.EXPAND)
		buttonSizer.Add(resignButton, 1, wx.ALL|wx.EXPAND)
		mainSizer.Add(buttonSizer,1,wx.ALL|wx.EXPAND)

		self.panel.SetSizer(mainSizer)
		
		passButton.Bind(wx.EVT_BUTTON, self.PassButtonClick)
		resignButton.Bind(wx.EVT_BUTTON, self.ResignButtonClick)

	def PassButtonClick(self,event):
		self.game_controller.pass_turn()

	def ResignButtonClick(self,event):
		self.game_controller.resign()

class GoApp(wx.App):
	def __init__(self, game_controller, colors):
		self.game_controller = game_controller
		self.colors = colors
		wx.App.__init__(self)

	def OnInit(self):
		'''For now, this will create a game view on startup. Later we will create all the widgets for starting games, and we will create GameViews when games are started.'''
		frame = GameViewWx(self.game_controller, self.colors)
		frame.Show(True)
		self.SetTopWindow(frame)
		return True

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)

#Test the display stuff only
if __name__ == '__main__':

	# Change on click behaviour
	def on_click(self,pos):
		'''Highlight the nearest point'''
		pos = self.view_to_grid(pos)
		self.highlighted = pos
		self.draw(False,True)
	GridViewPygame.on_click = on_click

	#Initialize pygame
	pygame.init()
	screen = pygame.display.set_mode((600, 300))

	#Create grid
	grid = geometry.FoldedGrid(5,5,1,[('N','S'),('E','W')])
	thegame = game.TwoPlayerGame(board.Board(grid))
	colors = {thegame.black:(0,0,0),thegame.white:(100,100,100)}
	view = GridViewPygame(thegame.board.grid, screen, zoom_to_fit=True, join_connected=True, highlight_connected=True, colors=colors, mainScreen=True)

	#Handle events
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				view.on_click(pygame.mouse.get_pos())
