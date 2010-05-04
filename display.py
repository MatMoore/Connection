import game
import board
import pygame
from pygame.locals import *
import geometry

class GridViewPygame:
	'''Draw grids using pygame'''

	def __init__(self, grid, surface, scale=None, rotation=0, zoom_to_fit=False, join_connected=False, highlight_connected=True, colors = {}):
		grid_width = max([x for x,y in grid.points])
		grid_height = max([y for x,y in grid.points])
		width = surface.get_width()
		height = surface.get_height()

		if zoom_to_fit:
			scale = min(width/float(grid_width), height/float(grid_height))
		elif scale is None:
			scale = 1

		self.scale = scale
		self.grid = grid
		self.surface = surface
		self.grid.register_listener(self.draw)
		self.highlighted = None

		self.highlight_connected = highlight_connected
		self.join_connected = join_connected

		self.colors = colors

	def draw(self, *args):
		'''Draw the grid'''
		#print 'redrawing'
		scale = self.scale
		self.surface.fill((255,255,255))

		for p in self.grid.points:
			x,y = p
			point = self.grid.get_point(x,y)
			x *= scale
			y *= scale

			if point in self.colors:
				pygame.draw.circle(self.surface, self.colors[point], (x,y), 5)
			else:
				pygame.draw.circle(self.surface, (0,0,0), (x,y), 2)

		#This actually draws the line for each connection twice but never mind
		if self.join_connected:
			for a,bs in self.grid.connections.items():
				for b in bs:
					ax,ay = a
					bx,by = b
					ax *= scale
					ay *= scale
					bx *= scale
					by *= scale
					pygame.draw.line(self.surface, (0,0,0), (ax,ay), (bx,by),4)
		if self.highlight_connected and self.highlighted:
			for x,y in self.grid.connections[self.highlighted]:
				x *= scale
				y *= scale
				pygame.draw.circle(self.surface, (0,255,0), (x,y), 2)

		pygame.display.flip()

	def board_to_grid(self, pos):
		'''Convert view coordinates to grid ones'''
		x,y = pos
		x = int(round(x/self.scale))
		y = int(round(y/self.scale))
		return (x,y)

	def onClick(self, pos):
		'''Highlight the nearest point'''
		pos = self.board_to_grid(pos)
		#print pos
		self.highlighted = pos
		self.draw(False,True)


if __name__ == '__main__':

	#Initialize pygame
	pygame.init()
	screen = pygame.display.set_mode((600, 300))

	#Create grid
#	grid = RectangularGrid(19,19)
	grid = geometry.FoldedGrid(5,5,1,[('N','S'),('E','W')])
#	grid = FoldedGrid(19,19,1,[],[('N','S'),('E','W')])
	thegame = game.TwoPlayerGame(board.Board(grid))
	colors = {thegame.black:(0,0,0),thegame.white:(100,100,100)}
	view = GridViewPygame(thegame.board.grid, screen, zoom_to_fit=True, join_connected=True, highlight_connected=True, colors=colors)

	view.draw()

	#Handle events
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				view.onClick(pygame.mouse.get_pos())
