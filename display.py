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

class PlayerPanel(wx.Panel):
	'''Show details about the players'''
	def __init__(self,controller,parent=None,id=wx.ID_ANY):
		wx.Panel.__init__(self,parent,id)
		playerSizer = wx.GridBagSizer(0,5)
		self.scoreDisplays = {}
		self.captureDisplays = {}
		self.timeDisplays = {}
		row = 0
		for i in controller.game.players:
			playerSizer.Add(wx.StaticText(self,wx.ID_ANY, i.name),(row,0),(1,2),flag=wx.ALIGN_CENTER_HORIZONTAL)
			row += 1
			capturesLabel = wx.StaticText(self, wx.ID_ANY, 'Captures:')
			scoreLabel = wx.StaticText(self, wx.ID_ANY, 'Score:')
			timeLabel = wx.StaticText(self, wx.ID_ANY, 'Time:')
			self.captureDisplays[i] = wx.StaticText(self,wx.ID_ANY,str(i.captures))
			self.scoreDisplays[i] = wx.StaticText(self,wx.ID_ANY,str(i.score))
			self.timeDisplays[i] = wx.StaticText(self,wx.ID_ANY,'All the time in the world')
			playerSizer.Add(capturesLabel,(row,0),(1,1),flag=wx.ALIGN_LEFT)
			playerSizer.Add(self.captureDisplays[i],(row,1),(1,1),flag=wx.ALIGN_LEFT)
			row += 1
			playerSizer.Add(scoreLabel,(row,0),(1,1),flag=wx.ALIGN_LEFT)
			playerSizer.Add(self.scoreDisplays[i],(row,1),(1,1),flag=wx.ALIGN_LEFT)
			row += 1
			playerSizer.Add(timeLabel,(row,0),(1,1),flag=wx.ALIGN_LEFT)
			playerSizer.Add(self.timeDisplays[i],(row,1),(1,1),flag=wx.ALIGN_LEFT)
			row += 1

			# Some space in between players
			playerSizer.Add((-1,30), (row,0), (1,2))
			row += 1
		self.SetSizer(playerSizer)
		#self.SetAutoLayout(True) # only needed if we call SetConstraints
		playerSizer.Fit(self) # Fit this panel to the minimum size of the sizer

		controller.game.register_listener(self.UpdateScore)

	def UpdateScore(self,move=None,*args):
		if move:
			self.captureDisplays[move.player].SetLabel(str(move.player.captures))
		else:
			for player in self.scoreDisplays.keys():
				self.scoreDisplays[player].SetLabel(str(player.score))

class BoardViewWx(wx.Panel):
	'''Show the board using wxPython'''

	def __init__(self, grid, colors, parent=None, id=wx.ID_ANY, bgColour=(255,255,255), borderWidth=0.75, stoneSpacing = 0.1, pointSize = 0.2, highlightColor = (255,255,0)):
		'''The border width defines an empty space bordering the outer edges, given in grid points. Stone spacing is the width in grid points of the space between neighbouring stones. Point size is given as a fraction of stone size.'''
		wx.Panel.__init__(self, parent, id, style=wx.FULL_REPAINT_ON_RESIZE)
		self.SetBackgroundColour(bgColour)
		self.colors = colors
		self.grid = grid
		self.grid.register_listener(self.BoardChanged)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnPaintBg)
		self.SetMinSize((100,100))

		# Tuples of pos, player indicating what the player is hovering over
		self._clicked = None
		self._hover = None

		self.stoneSpacing = stoneSpacing
		self.pointSize = pointSize
		self.highlightColor = highlightColor

		# Size of the board in grid spacings. Assumes an origin of 0,0
		self.grid_width = max([x for x,y in grid.points])
		self.grid_height = max([y for x,y in grid.points])

		self.borderWidth = borderWidth # width of border in grid units
		self.BoardChanged() # Make sure the board is drawn

		if self.IsDoubleBuffered():
			debug('Board view is using PaintDC')
		else:
			debug('Board view is using BufferedPaintDC')

	def BoardChanged(self,*args):
		self.Refresh() # trigger a paint event
		self.Update() # deal with it straight away

	def OnPaintBg(self, event):
		# Skip this and do all background stuff in OnPaint
		pass

	def OnPaint(self, event):
		'''Currently redraws the whole board. This could be optimised later to redraw changed areas only'''

		if self.IsDoubleBuffered():
			dc = wx.PaintDC(self)
		else:
			dc = wx.BufferedPaintDC(self) # device context

		dc.Clear()
		gc = wx.GraphicsContext.Create(dc) # graphics context

		stoneSize = self.StoneSize()
		pointSize = self.pointSize * stoneSize

		# Draw hovering stone
		hoverPos = None
		if self._hover:
			hoverPos,player = self._hover
		elif self._clicked:
			hoverPos,player = self._clicked
		if hoverPos is not None:
			x,y = self.GridToView(hoverPos)
			color = self.colors[player]
			gc.SetPen(wx.Pen("black", 0))
			gc.SetBrush(wx.Brush(color))
			gc.DrawEllipse(x-stoneSize/2, y-stoneSize/2, stoneSize, stoneSize)

		# Draw stones / points
		for p in self.grid.points:
			x,y = p
			value = self.grid.get_point(x,y)
			x,y = self.GridToView(p)

			if value is not None and value[0] in self.colors:
				player, dead = value
				gc.SetPen(wx.Pen(self.colors[player],0))
				gc.SetBrush(wx.Brush(self.colors[player]))
				gc.DrawEllipse(x-stoneSize/2, y-stoneSize/2, stoneSize, stoneSize)
			elif p != hoverPos:
				gc.SetPen(wx.Pen("black", 0))
				gc.SetBrush(wx.Brush("black"))
				gc.DrawEllipse(x-pointSize/2, y-pointSize/2, pointSize, pointSize)

#		if self.highlight_connected and self.highlighted:
#			debug('Highlighting connections for %s' % str(self.highlighted))
#			for c in self.grid.connections[self.highlighted]:
#				x,y = self.grid_to_view(c)
#				pygame.draw.circle(self.surface, (0,255,0), (int(x),int(y)), 2)

	def GridToView(self,pos):
		'''Convert grid coordinated to view ones'''
		x,y = pos
		width,height = self.GetClientSizeTuple()
		grid_width = self.grid_width + 2*self.borderWidth
		grid_height = self.grid_height + 2*self.borderWidth
		scale = min(width/float(grid_width), height/float(grid_height))
		return ((x+self.borderWidth)*scale, (y+self.borderWidth)*scale)

	def StoneSize(self):
		width,height = self.GetClientSizeTuple()
		grid_width = self.grid_width + 2*self.borderWidth
		grid_height = self.grid_height + 2*self.borderWidth
		scale = min(width/float(grid_width), height/float(grid_height))
		return max(4, scale*(1 - self.stoneSpacing))

	def ViewToGrid(self, pos):
		'''Convert view coordinates to grid ones'''
		x,y = pos
		width,height = self.GetClientSizeTuple()
		grid_width = self.grid_width + 2*self.borderWidth
		grid_height = self.grid_height + 2*self.borderWidth
		scale = min(width/float(grid_width), height/float(grid_height))
		x = int(round(x/scale-self.borderWidth))
		y = int(round(y/scale-self.borderWidth))

		# Return None if out of range
		if x > self.grid_width \
				or y > self.grid_height \
				or x < 0 \
				or y < 0:
			return None

		return (x,y)


class PlayableBoardWx(BoardViewWx):
	'''Playable board using wxPython'''
	def __init__(self, controller, colors, parent=None, id=wx.ID_ANY):
		BoardViewWx.__init__(self, controller.game.board.grid, colors, parent, id)
		self.controller = controller
		self.Bind(wx.EVT_LEFT_UP, self.MouseUp)
		self.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
		self.Bind(wx.EVT_MOTION, self.MouseMove)
		self.controller.register_listener(self.GameUpdated)

	def GameUpdated(self, accept_moves, *args):
		if not accept_moves:
			self._clicked = None
			self._hover = None
			self.Refresh()

	def MouseDown(self, event):
		'''Checks the game state and forwards the event to the correct event handler'''
		state = self.controller.game.state
		f = {
			game.PLAY_GAME: self.MouseDownGame
		}
		if state in f:
			f[state](event)

	def MouseUp(self, event):
		'''Checks the game state and forwards the event to the correct event handler'''
		state = self.controller.game.state
		f = {
			game.PLAY_GAME: self.MouseUpGame
		}
		if state in f:
			f[state](event)

	def MouseMove(self, event):
		'''Checks the game state and forwards the event to the correct event handler'''
		state = self.controller.game.state
		f = {
			game.PLAY_GAME: self.MouseMoveGame
		}
		if state in f:
			f[state](event)

	def MouseDownGame(self, event):
		event.Skip()

		pos = event.GetPositionTuple()
		pos = self.ViewToGrid(pos)
	
		# Ignore clicks in the border area
		if pos:
			x,y = pos
			self._clicked = pos,self.controller.game.next_player
			self._hover = None
			debug('clicked %d,%d' % pos)
			self.Refresh()

	def MouseMoveGame(self, event):
		pos = event.GetPositionTuple()
		pos = self.ViewToGrid(pos)

		# Ignore clicks in the border area
		if pos:
			x,y = pos
			if not self._clicked:
				self._hover = pos,self.controller.game.next_player
			self.Refresh()

	def MouseUpGame(self, event):
		'''Callback called when the user clicks in the window'''
		pos = event.GetPositionTuple()
		pos = self.ViewToGrid(pos)

		# Ignore clicks in the border area
		if pos:
			x,y = pos

			# Don't place a stone if the player clicked and dragged to a different point
			if self._clicked is not None and self._clicked[0] != pos:
				self._clicked = None
				self.Refresh()
				return

			debug('released at %d,%d' % (x,y))

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

			self._clicked = None

class GameViewWx(wx.Frame):
	def __init__(self,game_controller,colors,parent=None,id=wx.ID_ANY,title='Go'):
		wx.Frame.__init__(self,parent,id,title,size=(360,400))
		self.panel = wx.Panel(self, wx.ID_ANY)
		
		self.game_controller = game_controller
		board = PlayableBoardWx(game_controller,colors,self.panel)
		playerView = PlayerPanel(game_controller,self.panel)

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		otherMainSizer = wx.BoxSizer(wx.HORIZONTAL)
		otherMainSizer.Add(board,1,wx.EXPAND)
		otherMainSizer.Add(playerView,0,wx.EXPAND|wx.ALL,border=10)
		mainSizer.Add(otherMainSizer,1,wx.EXPAND)
		
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.passButton = wx.Button(self.panel, wx.ID_ANY, 'Pass')
		self.resignButton = wx.Button(self.panel, wx.ID_ANY, 'Resign')
		buttonSizer.Add(self.passButton, 1, wx.ALL|wx.FIXED_MINSIZE)
		buttonSizer.Add(self.resignButton, 1, wx.ALL|wx.FIXED_MINSIZE)
		mainSizer.Add(buttonSizer,0)

		self.panel.SetSizer(mainSizer)
		
		self.passButton.Bind(wx.EVT_BUTTON, self.PassButtonClick)
		self.resignButton.Bind(wx.EVT_BUTTON, self.ResignButtonClick)
		self.CreateStatusBar()
		self.UpdateStatus()

		# Update status whenever the game state changes
		self.game_controller.game.register_listener(self.UpdateStatus)

		# Grey out pass/resign if it's not the player's go
		self.game_controller.register_listener(self.GameUpdated)

	def UpdateStatus(self,move=None,*args):
		if move is None:
			moveTxt = ''
		else:
			moveTxt = 'Last move: ' + str(move).title() + ' -- '
		if self.game_controller.game.state == game.PLAY_GAME:
			gameTxt = self.game_controller.game.next_player.name + ' to play'
		elif self.game_controller.game.state == game.GAME_OVER:
			if self.game_controller.game.winner is None:
				gameTxt = 'Game Over: Jigo'
			else:
				gameTxt = 'Game Over: '+self.game_controller.game.winner.name + ' wins'
		elif self.game_controller.game.state == game.MARK_DEAD:
			gameTxt = 'Mark dead stones'
		elif self.game_controller.game.state == game.PLACE_HANDICAP:
			gameTxt = self.game_controller.game.next_player.name + ' to place handicap'
		else:
			gameTxt = ''

		self.SetStatusText(moveTxt+gameTxt)

	def GameUpdated(self, accept_moves, *args):
		'''Enable pass/resign only if we accept moves'''
		self.passButton.Enable(accept_moves)
		self.resignButton.Enable(accept_moves)

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
